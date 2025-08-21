"""Enum for process states."""

import enum


class ProcessState(enum.Enum):
  """Enum for process states."""

  OFFLINE = "OFFLINE"
  ONLINE = "ONLINE"
  STARTING_UP = "STARTING_UP"
  UNHEALTHY = "UNHEALTHY"
  CRASHED = "CRASHED"
  PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
  UNKNOWN = "UNKNOWN"
