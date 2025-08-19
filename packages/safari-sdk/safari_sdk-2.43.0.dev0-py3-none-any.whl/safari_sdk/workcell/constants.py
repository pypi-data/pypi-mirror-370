"""Constants used in Workcell Manager and Process Launcher."""

import datetime

from safari_sdk.protos.ui import robotics_ui_pb2
from safari_sdk.workcell import process_state

ProcessState = process_state.ProcessState

STANDARD_BUTTON_COLOR = robotics_ui_pb2.Color(
    red=0.145098, green=0.5058824, blue=0.8745098, alpha=1
)
STANDARD_SUB_BUTTON_COLOR = robotics_ui_pb2.Color(
    red=0.65, green=0.85, blue=1, alpha=1
)
CREATE_TICKET_BUTTON_COLOR = robotics_ui_pb2.Color(
    red=0.8, green=0.0, blue=0.0, alpha=1
)
EPISODE_TIME_FILE_PATH: str = "/tmp/log_episode_time.txt"
OPERATOR_PROCESSES_BUTTON_LABEL = "<color=white><b>Processes</b></color>"
CREATE_TICKET_BUTTON_LABEL = (
    "<color=white><b>Create Ticket</b></color>"
)
CREATE_TICKET_BUTTON_ID = "create_ticket_button"
create_ticket_button_spec = robotics_ui_pb2.UISpec(
    x=0.1,
    y=0.8,
    width=0.18,
    height=30,
    mode=robotics_ui_pb2.UIMode.UIMODE_HEADER,
    background_color=CREATE_TICKET_BUTTON_COLOR,
)
OPERATOR_EVENT_STATUS_FILE = "/persistent/logs/op_event_status.txt"
OPERATOR_EVENT_DROPDOWN_ID: str = "operator event"
TROUBLESHOOTING_DROPDOWN_ID: str = "troubleshooting:dropdown"
TROUBLESHOOTING_HARDWARE_FAILURE_DROPDOWN_ID: str = "hardware failure"
OPERATOR_NOTES_PROMPT_ID: str = "operator notes"
CREATE_TICKET_BUTTON_ID: str = "create_ticket_button"
OPERATOR_LOGOUT_BUTTON_ID: str = "logout1"
OPERATOR_LOGOUT_BUTTON_LABEL: str = "<color=white>Log out</color>"
OPERATOR_LOGIN_BUTTON_ID: str = "login1"
OPERATOR_LOGIN_PROMPT_MSG: str = "Enter username:"
UITEXT_FILE_PATH: str = "/tmp/uitext.txt"
OPERATOR_LOGIN_TEXT_SPEC: robotics_ui_pb2.UISpec = robotics_ui_pb2.UISpec(
    x=0.9,
    y=0.7,
    height=0.4,
    width=0.15,
    mode=robotics_ui_pb2.UIMODE_HEADER,
)
OPERATOR_LOGIN_BUTTON_SPEC: robotics_ui_pb2.UISpec = robotics_ui_pb2.UISpec(
    x=0.9,
    y=0.3,
    height=0.4,
    width=0.15,
    mode=robotics_ui_pb2.UIMODE_HEADER,
    background_color=STANDARD_BUTTON_COLOR,
)
OPERATOR_EVENT_FILEPATHS: list[str] = [
    OPERATOR_EVENT_STATUS_FILE,
    "~/persistent/logs/op_event_status.txt",
]
STATUS_DROPDOWN_SPEC: robotics_ui_pb2.UISpec = robotics_ui_pb2.UISpec(
    width=0.15,
    height=30,
    x=0.1,
    y=0.5,
    mode=robotics_ui_pb2.UIMODE_HEADER,
)

SINGLE_INSTANCE_LOCK_FILE: str = "/tmp/robotics_ui_process_launcher.lock"
PROCESS_LAUNCHER_LOG_FILE: str = (
    f"/tmp/robotics_ui_process_launcher_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)
PROCESS_BUTTON_START_X: float = 0.1
PROCESS_BUTTON_WIDTH: float = 0.2
PROCESS_BUTTON_HEIGHT: float = 0.08
PROCESS_COLLAPSE_BUTTON_ID: str = "collapse"
PROCESS_WARNING_DIALOG_ID: str = "process_warning"
PROCESS_CITC_CLIENT_PREFIX: str = "process_launcher_citc_client_"
PROCESS_STATE_TO_COLOR_MAP: dict[ProcessState, robotics_ui_pb2.Color] = {
    ProcessState.ONLINE: robotics_ui_pb2.Color(
        red=0.11, green=0.55, blue=0.24, alpha=1
    ),
    ProcessState.OFFLINE: robotics_ui_pb2.Color(
        red=0.5, green=0.53, blue=0.55, alpha=1
    ),
    ProcessState.CRASHED: robotics_ui_pb2.Color(
        red=0.77, green=0.13, blue=0.12, alpha=1
    ),
    ProcessState.STARTING_UP: robotics_ui_pb2.Color(
        red=0.26, green=0.52, blue=0.96, alpha=1
    ),
}
LOW_DISK_SPACE_THRESHOLD_PERCENTAGE: float = 10.0
SIZE_OF_GB: float = 1024**3
