"""Unit tests for workcell_manager_lib."""

import builtins
from importlib import resources
from os import path
import shutil
import threading
import time
from typing import NamedTuple
from unittest import mock

from absl import flags
from watchdog import observers

from absl.testing import absltest
from safari_sdk.orchestrator.helpers import orchestrator_helper
from safari_sdk.protos.ui import robotics_ui_pb2
from safari_sdk.ui import client
from safari_sdk.workcell import constants
from safari_sdk.workcell import ergo_lib
from safari_sdk.workcell import operator_event_lib
from safari_sdk.workcell import operator_event_logger_lib
from safari_sdk.workcell import ticket_lib
from safari_sdk.workcell import workcell_manager_lib


FLAGS = flags.FLAGS
FLAGS.mark_as_parsed()


class WorkcellManagerLibTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    FLAGS.api_key = 'test_api_key'
    with mock.patch.object(client, 'Framework') as mock_roboticsui:
      self._mock_roboticsui = mock_roboticsui.return_value
      with mock.patch.object(
          orchestrator_helper, 'OrchestratorHelper'
      ) as mock_orca_helper:
        self._mock_orca_helper = mock_orca_helper.return_value
        with mock.patch.object(shutil, 'disk_usage') as mock_disk_usage:
          # Simulate low disk space (5% free)
          disk_usage_return_mock = NamedTuple(
              'disk_usage_return_mock',
              [('total', int), ('used', int), ('free', int)],
          )
          mock_disk_usage.return_value = disk_usage_return_mock(
              total=1000, used=950, free=50
          )
          self._workcell_manager = workcell_manager_lib.WorkcellManager(
              robotics_platform='aloha',
              hostname='hostname',
              port=1234,
              robot_id='test_robot',
              event_logger=mock.Mock(
                  spec=operator_event_logger_lib.OperatorEventLogger
              ),
              use_singleton_lock=False,
              is_test=True,
              ergo_enabled=True,
          )

  def tearDown(self):
    super().tearDown()
    self._workcell_manager.stop()

  def test_start_orca_process_success(self):
    with mock.patch.object(
        orchestrator_helper, 'OrchestratorHelper'
    ) as mock_orca_helper_cls:
      mock_orca_helper = mock_orca_helper_cls.return_value
      mock_orca_helper.connect.return_value = mock.Mock(success=True)
      mock_orca_helper.get_current_connection.return_value = mock.Mock(
          server_connection='test_orca_service'
      )
      with mock.patch.object(
          ticket_lib, 'get_ticket_cli'
      ) as mock_get_ticket_cli:
        self._workcell_manager.start_orca_connection()
        mock_get_ticket_cli.assert_called_once()

  def test_start_orca_process_no_connection(self):
    with mock.patch.object(
        orchestrator_helper, 'OrchestratorHelper'
    ) as mock_orca_helper_cls:
      mock_orca_helper = mock_orca_helper_cls.return_value
      mock_orca_helper.connect.return_value = mock.Mock(success=False)
      self._mock_roboticsui.reset_mock()
      with mock.patch.object(
          ticket_lib, 'DummyTicketCli'
      ) as mock_dummy_ticket_cli_cls:
        self._workcell_manager.start_orca_connection()
        mock_dummy_ticket_cli_cls.assert_called_once()

  def test_create_operator_event_gui_elements(self):
    self._mock_orca_helper.load_rui_workcell_state.return_value = mock.Mock(
        success=True,
        workcell_state='Available',
    )
    self._workcell_manager.create_operator_event_gui_elements()
    self._mock_orca_helper.load_rui_workcell_state.assert_called_once_with(
        robot_id='test_robot'
    )
    self._mock_roboticsui.create_dropdown.assert_called_once_with(
        dropdown_id=constants.OPERATOR_EVENT_DROPDOWN_ID,
        title='Status Options',
        msg='Select Event Type',
        choices=workcell_manager_lib.workcell_status_list,
        submit_label='Submit',
        spec=robotics_ui_pb2.UISpec(
            width=0.15,
            height=30,
            x=0.1,
            y=0.5,
            mode=robotics_ui_pb2.UIMODE_HEADER,
        ),
        initial_value=operator_event_lib.WorkcellStatus.AVAILABLE.value,
    )
    self._mock_roboticsui.setup_header.assert_called_once_with(
        height=0.2,
        visible=True,
        collapsible=False,
        expandable=False,
        screen_scaling=True,
    )
    self._mock_roboticsui.create_or_update_text.assert_called_once_with(
        text_id='Status',
        text=('<size=80em>Available</size>'),
        spec=robotics_ui_pb2.UISpec(
            width=0.5,
            height=0.7,
            background_color=robotics_ui_pb2.Color(
                red=1.0, green=1.0, blue=1.0, alpha=1.0
            ),
            x=0.5,
            y=0.5,
            mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
        ),
    )

  @mock.patch.object(workcell_manager_lib.os.path, 'expanduser')
  @mock.patch.object(workcell_manager_lib.pathlib, 'Path')
  def test_update_dropdown_value(self, mock_path, mock_expanduser):
    value = 'test_choice'
    mock_expanduser.return_value = '/fake/path/status.txt'
    mock_file_obj = mock.MagicMock()
    mock_path.return_value = mock_file_obj
    self._mock_orca_helper.set_rui_workcell_state.return_value = mock.Mock(
        success=True,
    )
    self._workcell_manager.update_dropdown_value(value)

    # Check that the file was created and written to.
    mock_expanduser.assert_called_once()
    mock_path.assert_called_once_with('/fake/path/status.txt')
    mock_file_obj.parent.mkdir.assert_called_once_with(
        parents=True, exist_ok=True
    )
    mock_file_obj.write_text.assert_called_once_with(value)

    # Check that the text was updated in the UI.
    self._mock_orca_helper.set_rui_workcell_state.assert_called_once_with(
        robot_id='test_robot',
        workcell_state=value,
    )
    self._mock_roboticsui.create_or_update_text.assert_called_once_with(
        text_id='Status',
        text=(f'<size=80em>{value}</size>'),
        spec=robotics_ui_pb2.UISpec(
            width=0.5,
            height=0.7,
            background_color=robotics_ui_pb2.Color(
                red=1.0, green=1.0, blue=1.0, alpha=1.0
            ),
            x=0.5,
            y=0.5,
            mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
        ),
    )

  def test_login_and_logout(self):
    with mock.patch.object(
        threading.Timer, 'start'
    ) as mock_timer_start:
      user_id = 'test_user'
      mock_timer_start.return_value = None
      self.assertIsNone(self._workcell_manager.login_user)

      # Log in and trigger all expected events.
      self._workcell_manager.login_with_user_id(user_id)
      event_logger = self._workcell_manager.event_logger
      event_logger.set_ldap.assert_called_once_with(user_id)
      event_logger.create_ui_event.assert_called_once_with(
          event=operator_event_lib.UIEvent.LOGIN.value
      )
      event_logger.write_event.assert_called_once()
      self._mock_orca_helper.set_current_robot_operator_id.assert_called_once_with(
          operator_id=user_id
      )
      self.assertIsNotNone(self._workcell_manager._login_thread)

      # Reset the mock's call counts before the logout actions
      event_logger.reset_mock()
      self._mock_orca_helper.reset_mock()

      # Log out of the user.
      self._workcell_manager.logout()
      self.assertIsNone(self._workcell_manager.login_user)
      event_logger.create_ui_event.assert_called_once_with(
          event=operator_event_lib.UIEvent.LOGOUT.value
      )
      event_logger.write_event.assert_called_once()
      event_logger.clear_ldap.assert_called_once()
      event_logger.clear_reporting_ldap.assert_called_once()
      self._mock_orca_helper.set_current_robot_operator_id.assert_called_once_with(
          operator_id=''
      )
      self.assertIsNone(self._workcell_manager._login_thread)

  def test_update_timeout_process(self):
    with mock.patch.object(path, 'isdir', return_value=True):
      with mock.patch.object(
          observers, 'Observer', autospec=True
      ) as mock_observer:
        # Start timeout process when operator is in operation.
        mock_observer.return_value = mock.Mock()
        self._workcell_manager.workcell_status_pair.update_status_pair(
            status=operator_event_lib.WorkcellStatus.IN_OPERATION.value,
            logout_status=operator_event_lib.WorkcellStatus.AVAILABLE.value,
        )
        self._workcell_manager.update_timeout_process()
        self.assertFalse(
            self._workcell_manager._timeout_stop_event.wait(5.0),
            'Timeout thread did not start.',
        )
        self.assertIsNotNone(self._workcell_manager._timeout_thread)
        self.assertIsNotNone(self._workcell_manager._observer)

        # Stop timeout process when operator is not in operation.
        self._workcell_manager.workcell_status_pair.update_status_pair(
            status=operator_event_lib.WorkcellStatus.AVAILABLE.value,
            logout_status=operator_event_lib.WorkcellStatus.AVAILABLE.value,
        )
        self._workcell_manager.update_timeout_process()
        self.assertTrue(
            self._workcell_manager._timeout_stop_event.wait(5.0),
            'Timeout thread did not stop.',
        )
        self.assertIsNone(self._workcell_manager._timeout_thread)
        self.assertIsNone(self._workcell_manager._observer)

  def test_init_screen_callback(self):
    self._mock_roboticsui.callbacks = (
        workcell_manager_lib.WorkcellManager.UiCallbacks(self._workcell_manager)
    )
    with mock.patch.object(
        workcell_manager_lib.WorkcellManager,
        'create_operator_event_gui_elements',
        autospec=True,
    ) as mock_create_operator_event_gui_elements:
      self._mock_roboticsui.callbacks.init_screen(self._mock_roboticsui)
      mock_create_operator_event_gui_elements.assert_called_once()

  def test_button_pressed_callback(self):
    self._mock_roboticsui.callbacks = (
        workcell_manager_lib.WorkcellManager.UiCallbacks(self._workcell_manager)
    )
    with mock.patch.object(
        workcell_manager_lib.WorkcellManager,
        'logout',
        autospec=True,
    ) as mock_logout:
      self._mock_roboticsui.callbacks.button_pressed(
          button_id=constants.OPERATOR_LOGOUT_BUTTON_ID
      )
      mock_logout.assert_called_once()

    with mock.patch.object(
        ticket_lib, 'fill_ticket_form'
    ) as mock_fill_ticket_form:
      self._mock_roboticsui.callbacks.button_pressed(
          button_id=constants.CREATE_TICKET_BUTTON_ID
      )
      mock_fill_ticket_form.assert_called_once()

  def test_dropdown_pressed_callback(self):
    self._mock_roboticsui.callbacks = (
        workcell_manager_lib.WorkcellManager.UiCallbacks(self._workcell_manager)
    )

    # Test the operator event dropdown.
    with mock.patch.object(
        workcell_manager_lib.WorkcellManager,
        'update_timeout_process',
        autospec=True,
    ) as mock_update_timeout_process:
      with mock.patch.object(
          workcell_manager_lib.WorkcellManager,
          'update_dropdown_value',
          autospec=True,
      ) as mock_update_dropdown_value:
        # Test when troubleshooting is selected in the dropdown.
        dropdown_value = (
            operator_event_lib.WorkcellStatus.TROUBLESHOOTING_TESTING.value
        )
        self._mock_roboticsui.callbacks.dropdown_pressed(
            dropdown_id=constants.OPERATOR_EVENT_DROPDOWN_ID,
            choice=dropdown_value,
        )
        mock_update_timeout_process.assert_called_once()
        mock_update_dropdown_value.assert_called_once()
        self.assertEqual(
            self._workcell_manager.workcell_status_pair.status,
            dropdown_value,
        )
        self.assertEqual(
            self._workcell_manager.workcell_status_pair.logout_status,
            dropdown_value,
        )
        self._mock_roboticsui.create_dropdown.assert_called_once_with(
            dropdown_id=constants.TROUBLESHOOTING_DROPDOWN_ID,
            title='Selection',
            msg='Please select a troubleshooting item:',
            choices=self._workcell_manager.ui.callbacks.troubleshooting_choices,
            submit_label='Submit',
            spec=robotics_ui_pb2.UISpec(width=0.3, height=0.3, x=0.5, y=0.5),
        )

        # Test when another value is selected in the dropdown.
        mock_update_timeout_process.reset_mock()
        mock_update_dropdown_value.reset_mock()
        dropdown_value = (
            operator_event_lib.WorkcellStatus.AVAILABLE.value
        )
        self._mock_roboticsui.callbacks.dropdown_pressed(
            dropdown_id=constants.OPERATOR_EVENT_DROPDOWN_ID,
            choice=dropdown_value,
        )
        mock_update_timeout_process.assert_called_once()
        mock_update_dropdown_value.assert_called_once()
        event_logger = self._workcell_manager.event_logger
        event_logger.create_workcell_status_event.assert_called_once_with(
            event=dropdown_value,
            event_data='ops status',
        )
        event_logger.create_workcell_status_event.reset_mock()
        event_logger.write_event.assert_called_once()
        event_logger.write_event.reset_mock()

    # Test the troubleshooting dropdown.
    self._mock_roboticsui.create_dropdown.reset_mock()
    self._mock_roboticsui.callbacks.dropdown_pressed(
        dropdown_id=constants.TROUBLESHOOTING_DROPDOWN_ID,
        choice='Hardware Failure',
    )
    self._mock_roboticsui.create_dropdown.assert_called_once_with(
        dropdown_id=constants.TROUBLESHOOTING_HARDWARE_FAILURE_DROPDOWN_ID,
        title='Selection',
        msg='Please select a hardware failure item:',
        choices=self._workcell_manager.ui.callbacks.troubleshooting_hardware_failure_choices,
        submit_label='Submit',
        spec=robotics_ui_pb2.UISpec(width=0.3, height=0.3, x=0.5, y=0.5),
    )
    self._mock_roboticsui.callbacks.dropdown_pressed(
        dropdown_id=constants.TROUBLESHOOTING_DROPDOWN_ID,
        choice='Calibration',
    )
    event_logger = self._workcell_manager.event_logger
    event_logger.create_workcell_status_event.assert_called_once_with(
        event=operator_event_lib.WorkcellStatus.TROUBLESHOOTING_TESTING.value,
        event_data='Calibration',
    )
    event_logger.create_workcell_status_event.reset_mock()
    event_logger.write_event.assert_called_once()
    event_logger.write_event.reset_mock()

    # Test the troubleshooting hardware failure dropdown.
    event_logger.reset_mock()
    self._mock_roboticsui.callbacks.dropdown_pressed(
        dropdown_id=constants.TROUBLESHOOTING_HARDWARE_FAILURE_DROPDOWN_ID,
        choice='Finger',
    )
    event_logger.create_workcell_status_event.assert_called_once_with(
        event=operator_event_lib.WorkcellStatus.TROUBLESHOOTING_TESTING.value,
        event_data='Finger',
    )
    event_logger.write_event.assert_called_once()
    event_logger.write_event.reset_mock()

  def test_prompt_pressed_callback(self):
    self._mock_roboticsui.callbacks = (
        workcell_manager_lib.WorkcellManager.UiCallbacks(self._workcell_manager)
    )
    self._mock_roboticsui.callbacks.prompt_pressed(
        prompt_id=constants.OPERATOR_NOTES_PROMPT_ID,
        data='test_response',
    )
    event_logger = self._workcell_manager.event_logger
    event_logger.create_ui_event.assert_called_once_with(
        event=operator_event_lib.UIEvent.OTHER_EVENT.value,
        event_data='test_response',
    )
    event_logger.write_event.assert_called_once()

    with mock.patch.object(
        workcell_manager_lib.WorkcellManager,
        'login_with_user_id',
        autospec=True,
    ) as mock_login_with_user_id:
      self._mock_roboticsui.callbacks.prompt_pressed(
          prompt_id=constants.OPERATOR_LOGIN_BUTTON_ID,
          data='user_id',
      )
      mock_login_with_user_id.assert_called_once_with(
          self._workcell_manager, 'user_id'
      )

  def test_form_pressed_callback(self):
    self._mock_roboticsui.callbacks = (
        workcell_manager_lib.WorkcellManager.UiCallbacks(self._workcell_manager)
    )
    with mock.patch.object(
        ticket_lib, 'is_valid_ticket_form'
    ) as mock_is_valid_ticket_form:
      # Test when the ticket form is invalid.
      mock_is_valid_ticket_form.return_value = (False, '')
      self._mock_roboticsui.callbacks.form_pressed(
          form_id='ticket_form',
          results='results',
      )
      mock_is_valid_ticket_form.assert_called_once()
      self._mock_roboticsui.create_chat.assert_has_calls([
          mock.call(
              chat_id='create_ticket_window',
              title='Ticket Status',
              submit_label='',
              spec=robotics_ui_pb2.UISpec(
                  x=0.4,
                  y=0.7,
                  width=0.4,
                  height=0.4,
                  disabled=True,
              )
          ),
      ])
      self._mock_roboticsui.add_chat_line.assert_called_once()

      # Test when the ticket form is valid.
      with mock.patch.object(
          ticket_lib, 'prepare_ticket_form_for_user'
      ) as mock_prepare_ticket:
        self._mock_roboticsui.add_chat_line.reset_mock()
        mock_is_valid_ticket_form.reset_mock()
        mock_is_valid_ticket_form.return_value = (True, '')
        mock_prepare_ticket.return_value = 'test_ticket'
        self._workcell_manager.orca_client = mock.Mock()
        self._workcell_manager.orca_client.submit_ticket.return_value = (
            'test_ticket'
        )
        self._mock_roboticsui.callbacks.form_pressed(
            form_id='ticket_form',
            results='results',
        )
        mock_prepare_ticket.assert_called_once()
        mock_is_valid_ticket_form.assert_called_once()
        self._mock_roboticsui.add_chat_line.assert_called_once()

  def test_accumulate_episode_time(self):
    with mock.patch.object(path, 'exists') as mock_exists:
      with mock.patch.object(builtins, 'open') as mock_open:
        with mock.patch.object(time, 'time') as mock_time:
          # Test when the episode time file exists.
          mock_time.return_value = 100
          mock_exists.return_value = True
          self._workcell_manager._login_time = 0
          mock.mock_open(mock=mock_open, read_data='10 100 success')
          self._workcell_manager.accumulate_episode_time()
          mock_open.assert_called_once()
          mock_exists.assert_has_calls([
              mock.call(constants.EPISODE_TIME_FILE_PATH),
              mock.call(constants.EPISODE_TIME_FILE_PATH),
          ])
          self.assertEqual(
              self._workcell_manager._accumulated_total_episode_time, 90
          )
          self.assertEqual(
              self._workcell_manager._accumulated_successful_episode_time, 90
          )
          self._mock_roboticsui.create_or_update_text.assert_called_once_with(
              text_id='total_episode',
              text=(
                  '<color=white>hours collected: <color=green>00:01:30'
                  ' (success)</color> / 00:01:30 (all) | login timer :'
                  ' 00:01:40</color>'
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

          # Test when the episode time file does not exist.
          mock_exists.return_value = False
          self._mock_roboticsui.create_or_update_text.reset_mock()
          self._workcell_manager.accumulate_episode_time()
          self._mock_roboticsui.create_or_update_text.assert_called_once_with(
              text_id='total_episode',
              text=(
                  '<color=green> login timer :  00:01:40</color>'
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

  def test_display_message_basic(self):
    """Test the basic functionality of display_message."""
    with mock.patch.object(time, 'sleep') as mock_sleep:
      test_message = 'Test Message'
      test_text_id = 'test_id_123'
      test_timeout_str = '5'
      test_timeout_int = 5
      test_window_str = '0.4,0.2,0.1,0.8'  # w, h, x, y
      win_w, win_h, win_x, win_y = 0.4, 0.2, 0.1, 0.8
      self._workcell_manager.display_message(
          message=test_message,
          text_id=test_text_id,
          timeout=test_timeout_str,
          window=test_window_str,
      )
      self._mock_roboticsui.create_or_update_text.assert_called_once_with(
          text_id=test_text_id,
          text=test_message,
          spec=robotics_ui_pb2.UISpec(
              width=win_w,
              height=win_h,
              x=win_x,
              y=win_y,
              mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
              background_color=robotics_ui_pb2.Color(
                  red=1.0, green=0.0, blue=1.0, alpha=1.0
              ),
          ),
      )
      mock_sleep.assert_called_once_with(test_timeout_int)
      self._mock_roboticsui.remove_element.assert_called_once_with(test_text_id)

  def test_check_disk_space_percentage_low_space(self):
    with mock.patch.object(
        shutil, 'disk_usage'
    ) as mock_disk_usage, mock.patch.object(
        threading.Thread, 'start'
    ) as mock_thread_start:
      mock_thread_start.return_value = None
      # Simulate low disk space (5% free)
      disk_usage_return_mock = NamedTuple(
          'disk_usage_return_mock',
          [('total', int), ('used', int), ('free', int)],
      )
      mock_disk_usage.return_value = disk_usage_return_mock(
          total=1000, used=950, free=50
      )
      self._workcell_manager._check_disk_space_percentage()
      self._mock_roboticsui.create_dialog.assert_called_once_with(
          dialog_id='low_disk_space_alert',
          title='Low Disk Space',
          msg='Low disk space! Available: 5.00 %.Please free up some space.',
          buttons=['OK'],
          spec=mock.ANY,
      )

  def test_check_disk_space_percentage_sufficient_space(self):
    with mock.patch.object(
        shutil, 'disk_usage'
    ) as mock_disk_usage, mock.patch.object(
        threading.Thread, 'start'
    ) as mock_thread_start:
      mock_thread_start.return_value = None
      # Simulate sufficient disk space (20% free)
      disk_usage_return_mock = NamedTuple(
          'disk_usage_return_mock',
          [('total', int), ('used', int), ('free', int)],
      )
      mock_disk_usage.return_value = disk_usage_return_mock(
          total=1000, used=800, free=200
      )
      self._workcell_manager._check_disk_space_percentage()
      self._mock_roboticsui.create_dialog.assert_not_called()

  @mock.patch('pathlib.Path')
  def test_restore_operator_status_valid_content(
      self, mock_path
  ):
    mock_path.return_value.is_file.return_value = True
    mock_path.return_value.read_text.return_value = 'In Operation'
    self._workcell_manager.restore_operator_status()
    self.assertEqual(
        self._workcell_manager.workcell_status_pair.status, 'In Operation'
    )
    self.assertEqual(
        self._workcell_manager.workcell_status_pair.logout_status, 'Available'
    )

  @mock.patch('pathlib.Path')
  def test_restore_operator_status_file_not_found(
      self, mock_path
  ):
    mock_path.return_value.is_file.return_value = False
    self._workcell_manager.restore_operator_status()
    self.assertEqual(
        self._workcell_manager.workcell_status_pair.status, 'Available'
    )
    self.assertEqual(
        self._workcell_manager.workcell_status_pair.logout_status, 'Available'
    )

  @mock.patch('pathlib.Path')
  def test_restore_operator_status_file_empty(
      self, mock_path
  ):
    mock_path.return_value.is_file.return_value = True
    mock_path.return_value.read_text.return_value = ''
    self._workcell_manager.restore_operator_status()
    self.assertEqual(
        self._workcell_manager.workcell_status_pair.status, 'Available'
    )
    self.assertEqual(
        self._workcell_manager.workcell_status_pair.logout_status, 'Available'
    )

  @mock.patch('pathlib.Path')
  def test_restore_operator_status_file_invalid_content(
      self, mock_path
  ):
    mock_path.return_value.is_file.return_value = True
    mock_path.return_value.read_text.return_value = 'invalid_content'
    self._workcell_manager.restore_operator_status()
    self.assertEqual(
        self._workcell_manager.workcell_status_pair.status, 'Available'
    )
    self.assertEqual(
        self._workcell_manager.workcell_status_pair.logout_status, 'Available'
    )

  def test_set_dropdown_shortcuts(self):
    workcell_status_list = [
        status.value for status in operator_event_lib.WorkcellStatus
    ]
    self._workcell_manager.set_dropdown_shortcuts(True)
    self._mock_roboticsui.create_dropdown.assert_called_once_with(
        dropdown_id=constants.OPERATOR_EVENT_DROPDOWN_ID,
        title='Status Options',
        msg='Select Event Type',
        choices=workcell_status_list,
        submit_label='Submit',
        spec=mock.ANY,
        shortcuts=operator_event_lib.workcell_shortcut_dict,
        initial_value=mock.ANY,
    )
    self._mock_roboticsui.create_dropdown.reset_mock()
    self._workcell_manager.set_dropdown_shortcuts(False)
    self._mock_roboticsui.create_dropdown.assert_called_once_with(
        dropdown_id=constants.OPERATOR_EVENT_DROPDOWN_ID,
        title='Status Options',
        msg='Select Event Type',
        choices=workcell_status_list,
        submit_label='Submit',
        spec=mock.ANY,
        shortcuts=None,
        initial_value=mock.ANY,
    )

  def test_ergo_threads_lifecycle(self):
    """Test that ergo threads startup at login and terminate at logout."""
    self.assertIsNone(self._workcell_manager._ergo_period_thread)
    self.assertIsNone(self._workcell_manager._ergo_duration_thread)

    with mock.patch.object(
        threading.Timer, 'start'
    ) as mock_timer_start:
      mock_timer_start.return_value = None
      self._workcell_manager.login_with_user_id('test_user')
      self.assertIsNotNone(self._workcell_manager._ergo_period_thread)
      self.assertIsNotNone(self._workcell_manager._ergo_duration_thread)

    self._workcell_manager.logout()
    self.assertIsNone(self._workcell_manager._ergo_period_thread)
    self.assertIsNone(self._workcell_manager._ergo_duration_thread)

  # TODO: b/433795712 - Re-enable this test after looking into kokoro failures.
  # def test_ergo_period_color_change(self):
  #   """Test that the RUI element "ergo_period" changes color."""
  #   self._workcell_manager.login_with_user_id('test_user')
  #   self._workcell_manager._last_ergo_break_termination_time = (
  #       time.time() - 30
  #   )
  #   time.sleep(2)  # Wait for the thread to update the text.
  #   self._workcell_manager.ui.create_or_update_text.assert_called_with(
  #       text_id='ergo_period',
  #       text=mock.ANY,
  #       spec=robotics_ui_pb2.UISpec(
  #           width=0.22,
  #           height=0.15,
  #           x=0.095,
  #           y=0.3,
  #           mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
  #           background_color=ergo_lib.ERGO_REQUIREMENT_MET_COLOR,
  #       ),
  #   )
  #   self._workcell_manager._last_ergo_break_termination_time = (
  #       time.time() - 60 * 2
  #   )
  #   time.sleep(2)  # Wait for the thread to update the text.
  #   self._workcell_manager.ui.create_or_update_text.assert_called_with(
  #       text_id='ergo_period',
  #       text=mock.ANY,
  #       spec=robotics_ui_pb2.UISpec(
  #           width=0.22,
  #           height=0.15,
  #           x=0.095,
  #           y=0.3,
  #           mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
  #           background_color=ergo_lib.ERGO_RECOMMENDED_COLOR,
  #       ),
  #   )
  #   self._workcell_manager.logout()

  # def test_ergo_reminder_popup(self):
  #   """Test that the RUI element "Ergo Reminder" shows up."""
  #   self._workcell_manager.login_with_user_id('test_user')
  #   self._workcell_manager._login_time = (
  #       time.time() - 60 * 2
  #   )  # Simulate 2 minutes of login.
  #   time.sleep(120.0)
  #   self._workcell_manager.ui.create_dialog.assert_called_with(
  #       dialog_id=ergo_lib.ERGO_REMINDER_POPUP_ID,
  #       title='Ergo Reminder',
  #       msg=mock.ANY,
  #       buttons=['OK'],
  #       spec=robotics_ui_pb2.UISpec(width=0.4, height=0.2, x=0.5, y=0.5),
  #   )
  #   self._workcell_manager.ui.remove_element.assert_called_with(
  #       ergo_lib.ERGO_REMINDER_POPUP_ID
  #   )
  #   self._workcell_manager.logout()

  def test_show_ergo_reminder_popup(self):
    """Test that the RUI element "Ergo Reminder" shows up."""
    with mock.patch.object(resources, 'files') as mock_files, mock.patch.object(
        time, 'sleep'
    ) as mock_sleep:
      mock_files.return_value.joinpath.return_value.read_bytes.return_value = (
          b'test_image'
      )
      mock_sleep.return_value = None
      self._workcell_manager._ergo_images = ['test_image']
      self._workcell_manager._show_ergo_reminder_and_exercise_popup(
          'test_message'
      )
      self._mock_roboticsui.make_image_window.assert_called_with(
          window_id=ergo_lib.ERGO_IMAGE_WINDOW_ID,
          image=b'test_image',
          title='Ergo Exercise',
          spec=robotics_ui_pb2.UISpec(width=0.5, height=0.5, x=0.5, y=0.5),
      )
      self._mock_roboticsui.create_dialog.assert_called_with(
          dialog_id=ergo_lib.ERGO_REMINDER_POPUP_ID,
          title='Ergo Reminder',
          msg='test_message',
          buttons=['OK'],
          spec=robotics_ui_pb2.UISpec(width=0.4, height=0.2, x=0.5, y=0.5),
      )
      self._mock_roboticsui.remove_element.assert_has_calls([
          mock.call(ergo_lib.ERGO_REMINDER_POPUP_ID),
          mock.call(ergo_lib.ERGO_IMAGE_WINDOW_ID),
      ])

if __name__ == '__main__':
  absltest.main()
