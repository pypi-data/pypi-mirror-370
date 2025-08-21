"""Workcell Process class."""

import dataclasses
from safari_sdk.workcell import workcell_messages_lib


@dataclasses.dataclass
class WorkcellProcess:
  process_filename: str
  process_path: str
  process_args: list[str]
  start_warning_message: str | None = None
  stop_warning_message: str | None = None
  watchdog_state_conditions: (
      list[workcell_messages_lib.WorkcellMessage] | None
  ) = None
