"""Workcell messages library."""

import dataclasses

from safari_sdk.workcell import process_state

ProcessState = process_state.ProcessState


@dataclasses.dataclass
class WorkcellMessage:
  message_identifier_regex: str | tuple[str, ...]
  process_state: ProcessState


EMPTY_DICT = {}


def convert_workcell_messages_list_to_dict(
    workcell_messages_list: list[WorkcellMessage],
) -> dict[str | tuple[str, ...], ProcessState]:
  workcell_messages_dict = {}
  for workcell_message in workcell_messages_list:
    workcell_messages_dict[workcell_message.message_identifier_regex] = (
        workcell_message.process_state
    )
  return workcell_messages_dict


def get_workcell_messages_dict(
    workcell_messages_list: list[WorkcellMessage],
) -> dict[str | tuple[str, ...], ProcessState]:
  if workcell_messages_list:
    return convert_workcell_messages_list_to_dict(workcell_messages_list)
  return EMPTY_DICT
