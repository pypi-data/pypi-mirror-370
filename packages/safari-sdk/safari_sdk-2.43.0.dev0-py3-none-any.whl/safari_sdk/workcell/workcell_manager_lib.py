"""Manage the user interface for the workcell.

This class is responsible for connecting to the RoboticsUI and handling
interactions with the UI:
  - Creates buttons and console windows for launching processes
  - Submits tickets via orca
  - Sets and logs workcell status and operator events
  - Observes the status of data collection and handles login and logout timeout
"""

import datetime
from importlib import resources
import os
import pathlib
import shutil
import threading
import time

from watchdog import events
from watchdog import observers

from safari_sdk.orchestrator.helpers import orchestrator_helper
from safari_sdk.protos.ui import robotics_ui_pb2
from safari_sdk.ui import client
from safari_sdk.workcell import constants
from safari_sdk.workcell import ergo_lib
from safari_sdk.workcell import operator_event_lib
from safari_sdk.workcell import operator_event_logger_lib
from safari_sdk.workcell import process_launcher_lib
from safari_sdk.workcell import single_instance_lib
from safari_sdk.workcell import ticket_lib


_TIMEOUT_SECONDS: float = 30 * 60
_OBSERVER_DIR: str = "/persistent/logs/robup/in/"

status_event_map = operator_event_lib.workcell_status_event_dict
workcell_status_list = [
    status.value for status in operator_event_lib.WorkcellStatus
]


class SynchronizedPair:

  def __init__(self, status: str, logout_status: str):
    self.status = status
    self.logout_status = logout_status

  def update_status_pair(self, status: str, logout_status: str) -> None:
    self.status = status
    self.logout_status = logout_status


def get_y_position(height: float, idx: int) -> float:
  return (1 - height / 2) - height * idx


class WorkcellManager:
  """Manage starting and stopping of processes."""
  _timeout_thread: threading.Thread = None
  _timeout_stop_event: threading.Event = None
  _timeout_start_time: float = 0
  _login_time: float = 0
  _accumulated_successful_episode_time: float = 0
  _accumulated_total_episode_time: float = 0
  _login_thread: threading.Thread = None
  _observer: observers.Observer = None
  workcell_status_pair = SynchronizedPair(
      status="Task Setup/Change", logout_status="Available"
  )
  _robotics_platform: str = "NotSpecified"
  # Preferred method of get/set current operator ID.
  orca_helper: orchestrator_helper.OrchestratorHelper | None
  _check_disk_space_thread: threading.Thread = None
  _total_space_gb: float = 0
  process_launcher: process_launcher_lib.ProcessLauncher | None = None
  initialized: bool = False
  dropdown_value: str = operator_event_lib.WorkcellStatus.AVAILABLE.value

  _last_ergo_break_termination_time: float | None = None
  _total_ergo_break_duration: float = 0
  _ergo_period_thread: threading.Thread | None = None
  _ergo_duration_thread: threading.Thread | None = None
  _ergo_break_start_time: float | None = None
  _ergo_reminder_popup_shown: bool = False
  _ergo_parameters = ergo_lib.default_ergo_parameters
  _ergo_images: list[str] = []
  _ergo_image_idx: int = 0

  def __init__(
      self,
      robotics_platform: str,
      robot_id: str,
      hostname: str,
      port: int,
      event_logger: operator_event_logger_lib.OperatorEventLogger,
      use_singleton_lock: bool = False,
      is_test: bool = False,
      ergo_enabled: bool = False,
  ):
    self._robotics_platform = robotics_platform
    print(f"robotics_platform: {robotics_platform}")
    self.robot_id = robot_id
    print(f"robot_id: {self.robot_id}")
    self.hostname: str = hostname
    self._port = port

    lock_file = pathlib.Path(constants.SINGLE_INSTANCE_LOCK_FILE)
    self.use_singleton_lock = use_singleton_lock
    self.single_instance = single_instance_lib.SingleInstance(
        lock_file, self.use_singleton_lock
    )

    self.start_orca_connection()

    self.ui_exists: bool = False
    self.ui: client.Framework = client.Framework(
        callbacks=self.UiCallbacks(self),
    )

    self.ui.connect(host=self.hostname, port=self._port)
    self.ui.register_client_name("workcell_manager")
    self.login_user: str = None

    self.event_logger = event_logger
    self.restore_operator_status()
    self.update_timeout_process()
    self.initialized = True

    # Get the total disk space.
    try:
      disk_usage = shutil.disk_usage("/isodevice")
      self._total_space_gb = disk_usage.total / constants.SIZE_OF_GB
      if self._total_space_gb == 0:
        raise OSError("Total disk space is 0, aborting.")
    except OSError as e:
      print(f"Error checking disk space: {e}.")

    # If testing use shorter ergo durations
    if is_test:
      self._ergo_parameters = ergo_lib.test_ergo_parameters

    if ergo_enabled:
      if is_test:
        self._ergo_parameters = ergo_lib.test_ergo_parameters
      else:
        self._ergo_parameters = ergo_lib.ergo_enabled_parameters
    else:
      self._ergo_parameters = ergo_lib.ergo_disabled_parameters

    # Get the ergo images.
    self._ergo_images = ergo_lib.get_ergo_images()

  def start_orca_connection(self) -> None:
    """Starts the orca process."""
    self.orca_helper = orchestrator_helper.OrchestratorHelper(
        robot_id=self.robot_id,
        job_type=orchestrator_helper.JOB_TYPE.ALL,
        raise_error=False,
    )
    response = self.orca_helper.connect()
    if response.success:
      response = self.orca_helper.get_current_connection()
      orca_service = response.server_connection
      self.orca_client = ticket_lib.get_ticket_cli(orca_service)
      print("Created orca client.")
    else:
      self.orca_helper = None
      self.orca_client = ticket_lib.DummyTicketCli()
      print(
          f"Failed to connect to Orchestrator Service: {response.error_message}"
      )

  def restore_operator_status(self) -> None:
    """Restores the operator status from the status file."""
    op_status_file = pathlib.Path(constants.OPERATOR_EVENT_STATUS_FILE)
    if op_status_file.is_file():
      op_status_txt = op_status_file.read_text()
      if not op_status_txt or op_status_txt not in status_event_map:
        last_status = operator_event_lib.WorkcellStatus.AVAILABLE.value
        logout_status = status_event_map[last_status].logout_status.value
        print(
            "Operator status file found but was empty or had invalid content:"
            f" '{op_status_txt}'. Using default status: {last_status}"
        )
      else:
        last_status = op_status_txt
        print(f"Operator status file found: {op_status_txt}")
        logout_status = status_event_map[last_status].logout_status.value
      self.workcell_status_pair.update_status_pair(
          status=last_status, logout_status=logout_status
      )
    else:
      last_status = operator_event_lib.WorkcellStatus.AVAILABLE.value
      logout_status = status_event_map[last_status].logout_status.value
      print(
          f"Operator status file not found. Using default status: {last_status}"
      )
      self.workcell_status_pair.update_status_pair(
          status=last_status, logout_status=logout_status
      )

  def get_robotics_platform(self) -> str:
    return self._robotics_platform

  class UiCallbacks(client.UiCallbacks):
    """Callbacks for the project."""

    def __init__(self, script: "WorkcellManager"):
      """Stores a reference to the outer script."""
      self.script = script
      self.troubleshooting_choices: list[str] = [
          "Hardware Failure",
          "Unexpected Software Behavior",
          "Unexpected Robot Behavior",
          "Waiting for Eval Fix",
          "Calibration",
          "Task Feasibiity",
      ]
      self.troubleshooting_hardware_failure_choices: list[str] = [
          "Finger",
          "Hand",
          "Wrist",
          "Wrist Camera",
          "Head Camera",
          "Other",
      ]

    def init_screen(self, ui: client.Framework):
      """Called when the connection is made."""
      self.script.ui = ui
      print("I connected to the RoboticsUI!")
      self.script.create_operator_event_gui_elements()
      self.script.ui_exists = True
      self.script.ui.register_remote_command(
          "enable-dropdown-shortcuts",
          "Enable keyboard shortcuts for the workcell status dropdown.",
      )
      self.script.ui.register_remote_command(
          "disable-dropdown-shortcuts",
          "Disable keyboard shortcuts for the workcell status dropdown.",
      )
      self.script.ui.register_remote_command(
          "enable-sigkill",
          "Enable SIGKILL to stop processes.",
      )
      self.script.ui.register_remote_command(
          "disable-sigkill",
          "Disable SIGKILL to stop processes.",
      )
      if self.script.orca_helper is not None:
        self.script.ui.create_button_spec(
            constants.CREATE_TICKET_BUTTON_ID,
            constants.CREATE_TICKET_BUTTON_LABEL,
            spec=constants.create_ticket_button_spec,
        )
        self.script.ui.create_chat(
            chat_id="operator_event_spanner_submit_window",
            title="Operator Event Orca Logging",
            submit_label="",
            spec=robotics_ui_pb2.UISpec(
                x=0.4,
                y=0.7,
                width=0.4,
                height=0.4,
                disabled=True,
                minimized=True,
            ),
        )

    def ignore_on_not_initialized(func):  # pylint: disable=no-self-argument
      """Decorator to ignore calls if WorkcellManager is not initialized."""

      def wrapper(self, *args, **kwargs):
        if not self.script.initialized:
          return
        try:
          func(self, *args, **kwargs)
        except client.RoboticsUIConnectionError:
          # The connection may die during the call, which we can ignore since we
          # will be restoring the connection and reinitializing the UI
          # afterwards.
          return

      return wrapper

    @ignore_on_not_initialized
    def console_data_received(self, command: str):
      match command.strip():
        case "enable-dropdown-shortcuts":
          self.script.set_dropdown_shortcuts(True)
        case "disable-dropdown-shortcuts":
          self.script.set_dropdown_shortcuts(False)
        case "enable-sigkill":
          if self.script.process_launcher is not None:
            self.script.process_launcher.enable_sigkill(True)
            print("Enabled SIGKILL to stop processes.")
        case "disable-sigkill":
          if self.script.process_launcher is not None:
            self.script.process_launcher.enable_sigkill(False)
            print("Disabled SIGKILL to stop processes.")
        case _:
          pass

    @ignore_on_not_initialized
    def teleop_received(
        self, teleop_message: robotics_ui_pb2.TeleopMessage
    ) -> None:
      """Prevent teleop broadcast from spamming the terminal."""
      return

    @ignore_on_not_initialized
    def button_pressed(self, button_id: str) -> None:
      """Called when a button is pressed."""
      if self.script.process_launcher is not None:
        self.script.process_launcher.button_pressed(button_id)
      if button_id == constants.OPERATOR_LOGOUT_BUTTON_ID:
        self.script.logout()
        return
      if button_id == constants.CREATE_TICKET_BUTTON_ID:
        ticket_lib.fill_ticket_form(self.script.ui, self.script.robot_id)
        print("done with  action change")

    @ignore_on_not_initialized
    def dialog_pressed(self, dialog_id: str, choice: str) -> None:
      """Called when a dialog is submitted."""
      if self.script.process_launcher is not None:
        self.script.process_launcher.dialog_pressed(dialog_id, choice)

    @ignore_on_not_initialized
    def dropdown_pressed(
        self,
        dropdown_id: str,
        choice: str | list[str],
    ) -> None:
      """Called when one of the dropdown option is submitted."""
      # Execute below dropdown process only if the call originates from
      # the operator event dropdown
      if dropdown_id == constants.OPERATOR_EVENT_DROPDOWN_ID:
        print(f"Submission received for {dropdown_id}: {choice}")
        previous_status = self.script.workcell_status_pair.status
        logout_status = status_event_map[choice].logout_status.value
        self.script.workcell_status_pair.update_status_pair(
            status=choice,
            logout_status=logout_status,
        )
        # Ergo Update
        self.script.update_ergo_status(
            current_workcell_status=choice,
            previous_workcell_status=previous_status,
        )
        # Long term: workcell_status_pair should take a function object to set
        # the definition of update_status_pair, so update_timeout_process gets
        # called automatically whenever update_status_pair is.
        self.script.update_timeout_process()
        self.script.update_dropdown_value(choice)
        if (
            choice
            == operator_event_lib.WorkcellStatus.TROUBLESHOOTING_TESTING.value
        ):
          self.script.ui.create_dropdown(
              dropdown_id=constants.TROUBLESHOOTING_DROPDOWN_ID,
              title="Selection",
              msg="Please select a troubleshooting item:",
              choices=self.troubleshooting_choices,
              submit_label="Submit",
              spec=robotics_ui_pb2.UISpec(width=0.3, height=0.3, x=0.5, y=0.5),
          )
        else:
          self.script.event_logger.create_workcell_status_event(
              event=choice, event_data="ops status"
          )
          self.script.event_logger.write_event()
          self.script.send_spanner_event(event=choice, event_data="ops status")
          print("done with non-troubleshooting dropdown action change")
      elif dropdown_id == constants.TROUBLESHOOTING_DROPDOWN_ID:
        if choice == "Hardware Failure":
          self.script.ui.create_dropdown(
              dropdown_id=constants.TROUBLESHOOTING_HARDWARE_FAILURE_DROPDOWN_ID,
              title="Selection",
              msg="Please select a hardware failure item:",
              choices=self.troubleshooting_hardware_failure_choices,
              submit_label="Submit",
              spec=robotics_ui_pb2.UISpec(width=0.3, height=0.3, x=0.5, y=0.5),
          )
        else:
          ops_event_data = choice
          self.script.event_logger.create_workcell_status_event(
              event=operator_event_lib.WorkcellStatus.TROUBLESHOOTING_TESTING.value,
              event_data=ops_event_data,
          )
          self.script.event_logger.write_event()
          self.script.send_spanner_event(
              event=choice,
              event_data=ops_event_data,
          )
          print("done with troubleshooting dropdown action change")
      elif (
          dropdown_id == constants.TROUBLESHOOTING_HARDWARE_FAILURE_DROPDOWN_ID
      ):
        ops_event_data = choice
        self.script.event_logger.create_workcell_status_event(
            event=operator_event_lib.WorkcellStatus.TROUBLESHOOTING_TESTING.value,
            event_data=ops_event_data,
        )
        self.script.event_logger.write_event()
        self.script.send_spanner_event(
            event=choice,
            event_data=ops_event_data,
        )
        print(
            "done with troubleshooting hardware failure dropdown action change"
        )
      else:
        print(f"Unsupported dropdown choice: {dropdown_id}")

    @ignore_on_not_initialized
    def prompt_pressed(self, prompt_id: str, data: str) -> None:
      """Called when one of the prompt option is submitted."""
      print(f"\n\nSubmission received for {prompt_id}: {data}")

      if prompt_id == constants.OPERATOR_NOTES_PROMPT_ID:
        self.script.event_logger.create_ui_event(
            event=operator_event_lib.UIEvent.OTHER_EVENT.value,
            event_data=data,
        )
        self.script.event_logger.write_event()
        self.script.send_spanner_event(
            event=operator_event_lib.UIEvent.OTHER_EVENT.value,
            event_data=data,
        )
        print("done with prompt action change")
      elif prompt_id == constants.OPERATOR_LOGIN_BUTTON_ID:
        self.script.login_with_user_id(data)

    @ignore_on_not_initialized
    def form_pressed(self, form_id: str, results: str):
      """Called when a form is submitted."""
      if form_id == "ticket_form":
        self.script.ui.create_chat(
            chat_id="create_ticket_window",
            title="Ticket Status",
            submit_label="",
            spec=robotics_ui_pb2.UISpec(
                x=0.4,
                y=0.7,
                width=0.4,
                height=0.4,
                disabled=True,
            ),
        )
        ticket_valid, ticket_error_message = ticket_lib.is_valid_ticket_form(
            results
        )
        if not ticket_valid:
          self.script.ui.add_chat_line(
              chat_id="create_ticket_window",
              text=ticket_error_message,
          )
          return

        results = ticket_lib.prepare_ticket_form_for_user(
            results, login_user=self.script.login_user
        )
        try:
          ticket_submission_instant = datetime.datetime.now()
          formatted_ticket_submission_instant = (
              ticket_submission_instant.strftime("%Y-%m-%d %H:%M:%S")
          )
          ticket_id = self.script.orca_client.submit_ticket(results)
          self.script.ui.add_chat_line(
              chat_id="create_ticket_window",
              text=(
                  f"{formatted_ticket_submission_instant}: Submitted ticket"
                  f" with id: {ticket_id}\n"
              ),
          )
          print("done with ticket submission action change")
        except NotImplementedError as e:
          self.script.ui.add_chat_line(
              chat_id="create_ticket_window",
              text=f"Failed to submit ticket: {e}",
          )

    @ignore_on_not_initialized
    def ui_connection_died(self) -> None:
      print("Lost UI connection.")
      time.sleep(5)
      print("Shutting down process launcher.")
      self.script.ui_exists = False

  def stop(self) -> None:
    """Stops the process."""
    if self.process_launcher is not None:
      self.process_launcher.stop()
    self.ui.shutdown()
    self.stop_disk_space_check_thread()
    self.stop_timeout_thread()
    self.stop_login_thread()
    self.stop_ergo_threads()
    self.stop_observer()
    print("Stopping workcell manager.")

  def create_operator_event_gui_elements(self) -> None:
    """Creates workcell and operator event logging GUI elements."""
    # read the status from possible filepaths.
    for filename in constants.OPERATOR_EVENT_FILEPATHS:
      op_status = pathlib.Path(os.path.expanduser(filename))
      if op_status.is_file():
        op_status_txt = op_status.read_text()
        print(f"Found op status file: {filename} op status: {op_status_txt}")
        self.dropdown_value = op_status_txt
        break
      else:
        print(f"No op status file found: {filename}")

    # read from orca
    if self.orca_helper is not None:
      response = self.orca_helper.load_rui_workcell_state(
          robot_id=self.robot_id
      )
      if response.success and response.workcell_state:
        # TODO: Enable this once orca is ready.
        # self.dropdown_value = operator_event_lib.WorkcellStatus[
        #     response.workcell_state.removeprefix("RUI_WORKCELL_STATE_")
        # ].value
        print(f"Load workcell state from orca: {self.dropdown_value}")
      else:
        print(
            f"Failed to load workcell state from orca: {response.error_message}"
        )

    self.ui.create_dropdown(
        dropdown_id=constants.OPERATOR_EVENT_DROPDOWN_ID,
        title="Status Options",
        msg="Select Event Type",
        choices=workcell_status_list,
        submit_label="Submit",
        spec=constants.STATUS_DROPDOWN_SPEC,
        initial_value=self.dropdown_value
    )
    self.create_dropdown_display_text(self.dropdown_value)
    self.ui.setup_header(
        height=0.2,
        visible=True,
        collapsible=False,
        expandable=False,
        screen_scaling=True,
    )

  def create_dropdown_display_text(self, choice: str) -> None:
    """Called when one of the dropdown option is submitted."""
    if choice in status_event_map:
      color = status_event_map[choice].background_color
    else:
      print("Unsupported dropdown choice.")
      color = robotics_ui_pb2.Color(red=1.0, green=1.0, blue=1.0, alpha=1.0)
    self.ui.create_or_update_text(
        text_id="Status",
        text=("<size=80em>" + choice + "</size>"),
        spec=robotics_ui_pb2.UISpec(
            width=0.5,
            height=0.7,
            background_color=color,
            x=0.5,
            y=0.5,
            mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
        ),
    )

  def update_dropdown_value(self, data: str) -> None:
    """Called when one of the dropdown option is submitted."""
    result: str | None = None
    for filename in constants.OPERATOR_EVENT_FILEPATHS:
      try:
        file = pathlib.Path(os.path.expanduser(filename))
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(data)
        print(f"Saving file in '{filename}'")
        result = filename
        break
      except OSError as e:
        print(f"Error creating file in '{filename}': {e}")
    if result:
      print(f"File '{result}' written successfully.")
    else:
      print("Failed to write file. Operator event status will not be saved.")

    if self.orca_helper is not None:
      response = self.orca_helper.set_rui_workcell_state(
          robot_id=self.robot_id,
          workcell_state=data,
      )
      if response.success:
        print(f"Set workcell state in orca: {data}")
      else:
        print(
            f"Failed to set workcell state in orca: {response.error_message}"
        )
    self.dropdown_value = data
    self.create_dropdown_display_text(data)

  def login_with_user_id(self, user_id: str) -> None:
    """Logs in with the given user id and sends a login event."""
    # If the user is already logged in, log them out first.
    if self.login_user:
      self.logout()
    print(f"Logging in with user: {user_id}")
    self.login_user = user_id
    self.event_logger.set_ldap(user_id)
    self.event_logger.create_ui_event(
        event=operator_event_lib.UIEvent.LOGIN.value
    )
    self.event_logger.write_event()
    self._login_time = time.time()
    if self.orca_helper is not None:
      self.orca_helper.set_current_robot_operator_id(operator_id=user_id)
    self.update_login_process(login_time=self._login_time)
    print("Calling start_disk_space_check_thread")
    self.start_disk_space_check_thread()

  def logout(self) -> None:
    """Set the login user to None and send a logout event."""
    if not self.login_user:
      print("No user to log out of.")
      return
    print(f"Logging out of current user: {self.login_user}")
    self.login_user = None
    self.event_logger.create_ui_event(
        event=operator_event_lib.UIEvent.LOGOUT.value
    )
    self.ui.send_dropdown_pressed_event(
        constants.OPERATOR_EVENT_DROPDOWN_ID,
        self.workcell_status_pair.logout_status,
    )
    self.event_logger.write_event()
    self.event_logger.clear_ldap()
    self.event_logger.clear_reporting_ldap()
    self._login_time = 0
    if self.orca_helper is not None:
      self.orca_helper.set_current_robot_operator_id(operator_id="")
    self.update_login_process()
    self.stop_ergo_threads()

  def update_login_process(self, login_time: float = 0) -> None:
    """Called when login or logout button is pressed."""
    self._login_time = login_time
    if self._login_time != 0:
      self.start_login_thread()
    elif self._login_time == 0:
      self.stop_login_thread()
    else:
      print("No login or logout button pressed")

  def update_timeout_process(self) -> None:
    """Start or stop the timeout process when the workcell status is updated."""
    if not os.path.isdir(os.path.expanduser(_OBSERVER_DIR)):
      print(
          f"Logs directory '{_OBSERVER_DIR}' does not exist to be observed."
          " Auto-logout timer disabled."
      )
      return

    # Start timeout process only if the operator is in operation.
    if (
        self.workcell_status_pair.status
        == operator_event_lib.WorkcellStatus.IN_OPERATION.value
    ):
      self.start_timeout_thread()
      self.start_observer()
    else:
      self.stop_timeout_thread()
      self.stop_observer()

  def start_observer(self) -> None:
    """Start observer to watch for changes in the logs directory."""
    if self._observer is not None:
      return

    class ObserverHandler(events.FileSystemEventHandler):
      """Handler for file system events.

      This handler resets the timeout when a new file is created in the
      persistent logs directory.
      """

      _handler: WorkcellManager

      def __init__(self, handler: WorkcellManager):
        self._handler = handler

      def on_created(self, event):
        self._handler.reset_timeout()

    event_handler = ObserverHandler(self)
    self._observer = observers.Observer()
    self._observer.daemon = True
    self._observer.schedule(
        event_handler, os.path.expanduser(_OBSERVER_DIR), recursive=True
    )
    self._observer.start()
    print("Observer started...")

  def stop_observer(self) -> None:
    """Stops the observer."""
    if self._observer is None:
      return
    self._observer.stop()
    self._observer.join()
    self._observer = None
    print("Observer stopped...")

  def start_login_thread(self) -> None:
    """Starts the login thread."""
    if self._login_thread is not None:
      return
    self._login_thread = threading.Timer(
        interval=1.0, function=self._update_total_time
    )
    self._login_thread.start()
    print("Login Thread started...")
    self._start_ergo_threads()
    threading.Timer(interval=1.0, function=self._display_bash_text).start()
    print("Bash text display thread started...")

  def start_disk_space_check_thread(self) -> None:
    """Starts the disk space check thread."""
    print("Disk Space Check Thread attempt...")
    if self._check_disk_space_thread is not None:
      return
    print("Disk Space Check Thread starting...")
    self._check_disk_space_thread = threading.Timer(
        interval=1800.0, function=self._check_disk_space_percentage
    )
    self._check_disk_space_thread.start()

  def _update_total_time(self) -> None:
    """Updates the total time."""
    if self._login_thread is None:
      return
    self.accumulate_episode_time()
    threading.Timer(interval=1.0, function=self._update_total_time).start()

  def stop_login_thread(self) -> None:
    """Stops the login thread."""
    if self._login_thread is not None:
      self._login_thread = None
    print("Login Thread stopped...")

  def stop_disk_space_check_thread(self) -> None:
    """Stops the disk space check thread."""
    if self._check_disk_space_thread is not None:
      self._check_disk_space_thread = None
    print("Disk Space Check Thread stopped...")

  def display_message(
      self,
      message: str = "",
      text_id: str = "",
      timeout: str = "10",
      window: str = "",
  ) -> None:
    """Displays a message for timeout seconds."""
    print(
        f"Message displayed: {message},\n"
        f"Id displayed: {id},\n"
        f"Timeout: {timeout},\n"
        f"window displayed: {window}"
    )
    win_w, win_h, win_x, win_y = window.split(",")
    win_w = float(win_w)
    win_h = float(win_h)
    win_x = float(win_x)
    win_y = float(win_y)
    color = robotics_ui_pb2.Color(red=1.0, green=0.0, blue=1.0, alpha=1.0)
    self.ui.create_or_update_text(
        text_id=text_id,
        text=message,
        spec=robotics_ui_pb2.UISpec(
            width=win_w,
            height=win_h,
            x=win_x,
            y=win_y,
            mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
            background_color=color,
        ),
    )
    time.sleep(int(timeout))
    print("Message display complete.")
    self.ui.remove_element(text_id)

  def _display_bash_text(self) -> None:
    """Displays messages coming from bash script."""
    if os.path.exists(constants.UITEXT_FILE_PATH):
      with open(constants.UITEXT_FILE_PATH, "r") as f:
        lines = f.readlines()
      ## delete the file after reading.
      os.remove(constants.UITEXT_FILE_PATH)
      msg, text_id, timeout, window = lines[1].strip().split(":")

      display_thread = threading.Thread(
          target=self.display_message, args=(msg, text_id, timeout, window)
      )
      display_thread.start()
    threading.Timer(interval=2.0, function=self._display_bash_text).start()

  def accumulate_episode_time(self) -> None:
    """Accumulates the total episode time(success & fail)."""

    self._accumulated_total_episode_time = 0
    self._accumulated_successful_episode_time = 0
    if os.path.exists(constants.EPISODE_TIME_FILE_PATH):
      with open(constants.EPISODE_TIME_FILE_PATH, "r") as f:
        for line in f:
          if len(line.strip().split()) != 3:
            continue
          episode_start_time, episode_end_time, result = line.strip().split()
          episode_start_time = float(episode_start_time)
          episode_end_time = float(episode_end_time)
          if episode_start_time < self._login_time:
            continue
          self._accumulated_total_episode_time += (
              episode_end_time - episode_start_time
          )
          if result == "success":
            self._accumulated_successful_episode_time += (
                episode_end_time - episode_start_time
            )

    def format_time(seconds: float) -> str:
      seconds = round(seconds)
      hours = seconds // 3600
      seconds = seconds % 3600
      minutes = seconds // 60
      seconds = seconds % 60
      return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    if os.path.exists(constants.EPISODE_TIME_FILE_PATH):
      self.ui.create_or_update_text(
          text_id="total_episode",
          text=(
              "<color=white>hours collected: <color=green>"
              f"{format_time(self._accumulated_successful_episode_time)}"
              " (success)</color> / "
              f"{format_time(self._accumulated_total_episode_time)} (all) |"
              " login timer :"
              f" {format_time(time.time() - self._login_time)}</color>"
          ),
          spec=robotics_ui_pb2.UISpec(
              width=0.5,
              height=0.15,
              x=0.5,
              y=0.075,
              mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
              background_color=robotics_ui_pb2.Color(alpha=0),
          ),
      )
    else:
      self.ui.create_or_update_text(
          text_id="total_episode",
          text=(
              "<color=green> login timer : "
              f" {format_time(time.time() - self._login_time)}</color>"
          ),
          spec=robotics_ui_pb2.UISpec(
              width=0.5,
              height=0.15,
              x=0.5,
              y=0.075,
              mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
              background_color=robotics_ui_pb2.Color(alpha=0),
          ),
      )

  def start_timeout_thread(self) -> None:
    """Starts the timeout thread."""
    if self._timeout_thread is not None:
      return
    self._timeout_start_time = time.time()
    self._timeout_stop_event = threading.Event()
    self._timeout_thread = threading.Thread(target=self._update_timeout_thread)
    self._timeout_thread.start()
    print("Timeout started...")

  def stop_timeout_thread(self) -> None:
    """Stops the timeout thread."""
    if (
        self._timeout_stop_event is not None
        and not self._timeout_stop_event.is_set()
    ):
      self._timeout_stop_event.set()
      print("Timeout stopped...")
    if self._timeout_thread is not None:
      self._timeout_thread = None

  def reset_timeout(self) -> None:
    """Resets the timeout."""
    self._timeout_start_time = time.time()

  def set_dropdown_shortcuts(self, enabled: bool) -> None:
    """Whether to enable keyboard shortcuts for the workcell status dropdown."""
    shortcuts = operator_event_lib.workcell_shortcut_dict if enabled else None
    self.ui.create_dropdown(
        dropdown_id=constants.OPERATOR_EVENT_DROPDOWN_ID,
        title="Status Options",
        msg="Select Event Type",
        choices=workcell_status_list,
        submit_label="Submit",
        spec=constants.STATUS_DROPDOWN_SPEC,
        shortcuts=shortcuts,
        initial_value=self.dropdown_value,
    )
    print(
        f"{'Enable' if enabled else 'Disable'} keyboard shortcuts for the"
        " workcell status dropdown."
    )

  def _update_timeout_thread(self) -> None:
    """Updates the timeout thread and exit when timeout is reached."""
    while not self._timeout_stop_event.is_set():
      remaining = _TIMEOUT_SECONDS - (time.time() - self._timeout_start_time)
      if remaining <= 0:
        self.stop_timeout_thread()
        self.stop_observer()
        self.ui.send_button_pressed_event(constants.OPERATOR_LOGOUT_BUTTON_ID)
        print("Timeout...")
        break
      time.sleep(0.1)

  def _check_disk_space_percentage(self) -> None:
    """Checks for low disk space and alerts the user if needed."""
    print("Checking disk space percentage...")
    try:
      disk_usage = shutil.disk_usage("/isodevice")
      free_space_gb = disk_usage.free / constants.SIZE_OF_GB
      free_space_percentage = (free_space_gb / self._total_space_gb) * 100
      print(f"Total disk space: {self._total_space_gb:.2f} GB.")
      print(f"Free disk space: {free_space_gb:.2f} GB.")
      print(f"Free disk space percentage: {free_space_percentage:.2f} %.")
      if free_space_percentage < constants.LOW_DISK_SPACE_THRESHOLD_PERCENTAGE:
        self.ui.create_dialog(
            dialog_id="low_disk_space_alert",
            title="Low Disk Space",
            msg=(
                f"Low disk space! Available: {free_space_percentage:.2f} %."
                "Please free up some space."
            ),
            buttons=["OK"],
            spec=robotics_ui_pb2.UISpec(width=0.4, height=0.2, x=0.5, y=0.5),
        )
      threading.Timer(
          interval=1800.0, function=self._check_disk_space_percentage
      ).start()
    except OSError as e:
      print(f"Error checking disk space: {e}")
    except ZeroDivisionError as e:
      print(f"Error checking disk space: {e}. Total disk space is zero.")
      raise

  def send_spanner_event(self, event: str, event_data: str) -> None:
    """Sends a spanner event."""
    if self.orca_helper is not None:
      print("Logging to orca")
      add_event_response = self.orca_helper.add_operator_event(
          operator_event_str=event,
          operator_id=self.login_user,
          event_timestamp=int(time.time_ns()),
          resetter_id=self.login_user,
          event_note=event_data,
      )
      print("Logged to orca")
      print(f"add_event_response: {add_event_response}")
      self.ui.add_chat_line(
          chat_id="operator_event_spanner_submit_window",
          text=(
              "Operator Event Submission status:"
              f" {add_event_response.success}.\nError message:"
              f" {add_event_response.error_message}\n"
          ),
      )

  def update_ergo_status(
      self, current_workcell_status: str, previous_workcell_status: str
  ) -> None:
    """Updates the ergo status."""
    if (
        current_workcell_status
        == operator_event_lib.WorkcellStatus.ERGO_BREAK.value
    ):
      self._ergo_break_start_time = time.time()
      self.ui.remove_element(ergo_lib.ERGO_REMINDER_POPUP_ID)
    elif (
        previous_workcell_status ==
        operator_event_lib.WorkcellStatus.ERGO_BREAK.value
    ):
      if self._ergo_break_start_time is not None:
        ergo_break_duration = time.time() - self._ergo_break_start_time
        self._total_ergo_break_duration += ergo_break_duration
        self._last_ergo_break_termination_time = time.time()
        self._ergo_break_start_time = 0
    else:
      print(
          "No ergo break status update for current workcell status:"
          f" {current_workcell_status} and previous workcell status:"
          f" {previous_workcell_status}"
      )

  def _start_ergo_threads(self) -> None:
    """Starts the ergo threads."""
    if self._ergo_parameters == ergo_lib.ergo_disabled_parameters:
      print("Ergo threads not started because ergo is disabled.")
      return
    if self._ergo_period_thread is not None:
      return
    self._ergo_period_thread = threading.Thread(
        target=self._update_ergo_period_display
    )
    self._ergo_period_thread.start()
    print("Ergo Period Thread started...")
    if self._ergo_duration_thread is not None:
      return
    self._ergo_duration_thread = threading.Thread(
        target=self._check_ergo_duration
    )
    self._ergo_duration_thread.start()
    print("Ergo Duration Thread started...")

  def _update_ergo_period_display(self) -> None:
    """Updates the ergo period display."""
    while True:
      if self._login_thread is None:
        return
      if (
          self.workcell_status_pair.status
          == operator_event_lib.WorkcellStatus.ERGO_BREAK.value
      ):
        time_since_last_break = 0
      elif self._last_ergo_break_termination_time is not None:
        time_since_last_break = (
            time.time() - self._last_ergo_break_termination_time
        )
      else:
        time_since_last_break = time.time() - self._login_time
      minutes = int(time_since_last_break / 60)
      seconds = int(time_since_last_break % 60)
      text = f"Time since last break: {minutes:02d}:{seconds:02d}"
      color = ergo_lib.ERGO_REQUIREMENT_MET_COLOR
      if minutes >= int(
          self._ergo_parameters.alert_delay_seconds / 60
      ):  # Needs input
        color = ergo_lib.ERGO_RECOMMENDED_COLOR
      self.ui.create_or_update_text(
          text_id="ergo_period",
          text=text,
          spec=robotics_ui_pb2.UISpec(
              width=0.22,
              height=0.15,
              x=0.095,
              y=0.3,
              mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
              background_color=color,
          ),
      )
      time.sleep(1)

  def _check_ergo_duration(self) -> None:
    """Checks the ergo duration and shows a popup if needed."""
    while True:
      if self._login_thread is None:
        return
      if self._login_time == 0:
        self._ergo_reminder_popup_shown = False
        time.sleep(1)
        continue

      login_duration = time.time() - self._login_time
      non_ergo_login_duration = login_duration - self._total_ergo_break_duration
      non_ergo_login_duration_minutes = int(non_ergo_login_duration / 60)

      total_ergo_break_duration_minutes = int(
          self._total_ergo_break_duration / 60
      )
      required_ergo_duration_minutes = (
          self._ergo_parameters.get_required_break_minutes(
              non_ergo_login_duration_minutes
          )
      )

      if total_ergo_break_duration_minutes < required_ergo_duration_minutes:
        remaining_ergo_duration_minutes = (
            required_ergo_duration_minutes - total_ergo_break_duration_minutes
        )
        print(f"Current status: {self.workcell_status_pair.status}")
        if (
            self.workcell_status_pair.status
            != operator_event_lib.WorkcellStatus.ERGO_BREAK.value
        ):
          msg = ergo_lib.ERGO_BREAK_REQUIRED_MESSAGE.format(
              time_worked=non_ergo_login_duration_minutes,
              time_required=remaining_ergo_duration_minutes,
          )
          self._show_ergo_reminder_and_exercise_popup(msg)
      time.sleep(1)

  def stop_ergo_threads(self) -> None:
    """Stops the ergo threads."""
    if self._ergo_period_thread is not None:
      self._ergo_period_thread = None
      print("Ergo Period Thread stopped...")
    if self._ergo_duration_thread is not None:
      self._ergo_duration_thread = None
      print("Ergo Duration Thread stopped...")
    self._last_ergo_break_termination_time = None
    self._total_ergo_break_duration = 0
    self._ergo_break_start_time = None
    self._ergo_reminder_popup_shown = False

  def _show_ergo_reminder_and_exercise_popup(self, msg: str) -> None:
    """Shows the ergo reminder popup."""
    print("Showing ergo reminder popup")
    self.ui.remove_element(ergo_lib.ERGO_REMINDER_POPUP_ID)
    self.ui.create_dialog(
        dialog_id=ergo_lib.ERGO_REMINDER_POPUP_ID,
        title="Ergo Reminder",
        msg=msg,
        buttons=["OK"],
        spec=robotics_ui_pb2.UISpec(width=0.4, height=0.2, x=0.5, y=0.5),
    )

    print("Show ergo exercise popup")
    self.ui.remove_element(ergo_lib.ERGO_IMAGE_WINDOW_ID)
    if not self._ergo_images:
      print("No ergo images found to display.")
    else:
      image_name = self._ergo_images[self._ergo_image_idx]
      try:
        anchor_pkg = "google3.third_party.safari.sdk.safari.workcell"
        image_jpeg_bytes = (
            resources.files(anchor_pkg)
            .joinpath("ergo", "images", image_name)
            .read_bytes()
        )
      except (ModuleNotFoundError, FileNotFoundError) as e:
        print(f"Error reading image resource {image_name}: {e}")
        return

      self.ui.make_image_window(
          window_id=ergo_lib.ERGO_IMAGE_WINDOW_ID,
          image=image_jpeg_bytes,
          title="Ergo Exercise",
          spec=robotics_ui_pb2.UISpec(width=0.5, height=0.5, x=0.5, y=0.5),
      )
      self._ergo_image_idx = (self._ergo_image_idx + 1) % len(self._ergo_images)

    time.sleep(self._ergo_parameters.popup_delay_seconds)

