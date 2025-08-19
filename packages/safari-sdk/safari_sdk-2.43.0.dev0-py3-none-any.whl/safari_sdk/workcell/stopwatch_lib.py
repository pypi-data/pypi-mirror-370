"""Stopwatch class for tracking elapsed time.

Importing library/binary can create Stopwatch objects which are set with alarm
interval and callback. The callback is triggered when the alarm time is
exceeded.

Post every alarm, the Stopwatch is set back by the alarm interval.

Importing code can also pause and resume the stopwatch.
"""

import threading
import time
from typing import Callable


class Stopwatch:
  """Stopwatch class for tracking elapsed time."""

  def __init__(
      self,
      alarm_time_minutes: float = 30.0,
      timer_interval_seconds: float = 1.0,
      alarm_callback: Callable[..., None] | None = None,
  ):
    self._start_time: float | None = None
    self._elapsed_time: float = 0.0
    self._is_running = False
    self._pause_time: float | None = None
    self._accumulated_pause_time: float = 0.0
    self._timestepping_thread: threading.Thread | None = None
    self._stop_event = threading.Event()
    self._alarm_time_seconds: float = alarm_time_minutes * 60
    self._timer_interval_seconds: float = timer_interval_seconds
    self._alarm_triggered = False
    self._alarm_callback = alarm_callback

  def start(self):
    """Starts the stopwatch."""
    if self._timestepping_thread is None:
      self._start_time = time.time()
      self._elapsed_time = 0.0
      self._accumulated_pause_time = 0.0
      self._pause_time = None
      self._is_running = True
      self._alarm_triggered = False
      self._stop_event.clear()
      self._timestepping_thread = threading.Thread(target=self._timer_loop)
      self._timestepping_thread.start()
      print("Stopwatch started.")
    else:
      print("Stopwatch is already running or not properly stopped.")

  def _timer_loop(self):
    """Main loop for updating elapsed time and checking alarm."""
    while not self._stop_event.is_set():
      if self._is_running:
        now = time.time()
        self._elapsed_time = (
            now - self._start_time
        ) - self._accumulated_pause_time
        if not self._alarm_triggered:
          self._check_alarm()
      time.sleep(self._timer_interval_seconds)

  def reset(self):
    """Resets the stopwatch. Does not stop or start the timer thread."""
    self._start_time = time.time()
    self._elapsed_time = 0
    self._pause_time = None
    self._accumulated_pause_time = 0
    self._alarm_triggered = False
    if not self._is_running:
      self._pause_time = self._start_time
    print("Stopwatch reset.")

  def _check_alarm(self):
    if self._elapsed_time > self._alarm_time_seconds:
      print(f"Alarm triggered: {self._elapsed_time:.2f} seconds")
      self._alarm_triggered = True
      if self._alarm_callback:
        self._alarm_callback()
      self.reset()

  def pause(self):
    """Pauses the stopwatch."""
    if self._is_running:
      self._pause_time = time.time()
      self._is_running = False
      print("Stopwatch paused.")
    else:
      print("Stopwatch is not running or already paused.")

  def resume(self):
    """Resumes the stopwatch."""
    if not self._is_running and self._start_time is not None:
      if self._pause_time is not None:
        self._accumulated_pause_time += time.time() - self._pause_time
        self._pause_time = None
      self._is_running = True
      print("Stopwatch resumed.")
    elif self._is_running:
      print("Stopwatch is already running.")
    else:
      print("Stopwatch has not been started yet.")

  def stop(self):
    """Stops the stopwatch and terminates the timer thread."""
    if self._is_running:
      self._stop_event.set()
    if self._timestepping_thread is not None:
      self._timestepping_thread.join()
      self._timestepping_thread = None
      self._is_running = False
      self._start_time = None
      print("Stopwatch stopped.")
    else:
      print("Stopwatch is not running.")

  def get_elapsed_time(self) -> float:
    return self._elapsed_time
