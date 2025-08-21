"""Logger for logging to a file and to stdout."""

from typing import TextIO


class Logger:
  """Logs to a file and to stdout."""

  def __init__(self, *streams: TextIO):
    self.streams = streams

  def write(self, data: str) -> None:
    for stream in self.streams:
      stream.write(data)
      stream.flush()

  def flush(self) -> None:
    for stream in self.streams:
      stream.flush()
