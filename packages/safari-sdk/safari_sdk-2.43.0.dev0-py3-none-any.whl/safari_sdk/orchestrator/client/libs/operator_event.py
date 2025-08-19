# Copyright 2025 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Operator Event API for interacting with the spanner database via the orchestrator server."""

from googleapiclient import discovery
from googleapiclient import errors

from safari_sdk.orchestrator.client.dataclass import api_response
from safari_sdk.protos import operator_event_pb2

_RESPONSE = api_response.OrchestratorAPIResponse

_ERROR_NO_ORCHESTRATOR_CONNECTION = (
    "OrchestratorCurrentRobotInfo: Orchestrator connection is invalid."
)

_ERROR_RECORD_OPERATOR_EVENT = (
    "OrchestratorOperatorEvent: Error in recording operator event.\n"
)

operator_event_str_to_enum = {
    "Ergo Break": operator_event_pb2.OPERATOR_EVENT_TYPE_BREAK_ERGO,
    "Other Break": operator_event_pb2.OPERATOR_EVENT_TYPE_BREAK_OTHER,
    "Workcell Clean": operator_event_pb2.OPERATOR_EVENT_TYPE_WORKCELL_CLEANUP,
    "Troubleshooting Testing": (
        operator_event_pb2.OPERATOR_EVENT_TYPE_TROUBLESHOOTING_TESTING
    ),
    "Other": operator_event_pb2.OPERATOR_EVENT_TYPE_OTHER,
    "Reset Feedback": operator_event_pb2.OPERATOR_EVENT_TYPE_RESET_FEEDBACK,
    "Eval Policy Troubleshooting": (
        operator_event_pb2.OPERATOR_EVENT_TYPE_EVAL_POLICY_TROUBLESHOOTING
    ),
    "Task Feasibility": operator_event_pb2.OPERATOR_EVENT_TYPE_TASK_FEASIBILITY,
}


class OrchestratorOperatorEvent:
  """Operator Event API client for interacting with the spanner database via the orchestrator server."""

  def __init__(
      self, *, connection: discovery.Resource, robot_id: str,
  ):
    """Initializes the robot job handler."""
    self._connection = connection
    self._robot_id = robot_id

  def disconnect(self) -> None:
    """Clears current connection to the orchestrator server."""
    self._connection = None

  def add_operator_event(
      self,
      operator_event_str: str,
      operator_id: str,
      event_timestamp: int,
      resetter_id: str,
      event_note: str,
  ) -> _RESPONSE:
    """Set the current operator ID for the robot."""

    if self._connection is None:
      return _RESPONSE(error_message=_ERROR_NO_ORCHESTRATOR_CONNECTION)

    if operator_event_str not in operator_event_str_to_enum:
      return _RESPONSE(
          error_message=(
              _ERROR_RECORD_OPERATOR_EVENT
              + f"Operator event type {operator_event_str} is not supported."
          )
      )
    else:
      operator_event_type = operator_event_str_to_enum[operator_event_str]

      body = {
          "operator_event": {
              "robotId": self._robot_id,
              "eventType": operator_event_type,
              "eventEpochMicros": event_timestamp,
              "operatorId": operator_id,
              "resetterId": resetter_id,
              "note": event_note,
          }
      }
      print("body: ")
      print(body)

      try:
        response = (
            self._connection.orchestrator()
            .addOperatorEvent(body=body)
            .execute()
        )
      except errors.HttpError as e:
        return _RESPONSE(
            error_message=(
                _ERROR_RECORD_OPERATOR_EVENT
                + f"Reason: {e.reason}\nDetail: {e.error_details}"
            )
        )

    print("response: ")
    print(response)
    return _RESPONSE(
        success=response["success"],
    )
