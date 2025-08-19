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

"""An interface to the Logitech F710 that uses the joystick_evdev library."""

import copy

from safari_sdk.ui.input_devices import joystick_evdev

_F710_DEVICE_NAME_FILTER = 'Logitech Gamepad F710'

# Axis order: left-hand stick (L) first, right-hand stick (R) second.
# Stick axis order is left-right, up-down, left-trigger.
# Remapping first 3 axes to:
# left-right(L) up-down(L) left-right(R) up-down(R) left-trigger right-trigger.
_AXIS_REMAPPING = [0, 1, 3, 4, 2, 5]

# Moving sticks to the right and down returns positive values.
# Moving sticks to the left and up returns negative values.
# Inversion of axes applied to match the right-hand rule coordinate system.
# This means moving the sticks to the left and up returns positive values.
_AXIS_INVERT = [-1, -1, -1, -1, 1, 1]

_DEFAULT_TIMEOUT_SECONDS = 50.0 / 1000.0  # 50ms

_MAX_JOYSTICK_VALUE = 32767.0

_BUTTON_X = 307
_BUTTON_Y = 308
_BUTTON_B = 305
_BUTTON_A = 304
_BUTTON_LB = 310
_BUTTON_RB = 311

INDEX_BUTTON_X = 0
INDEX_BUTTON_Y = 1
INDEX_BUTTON_B = 2
INDEX_BUTTON_A = 3
INDEX_BUTTON_LB = 4
INDEX_BUTTON_RB = 5

_KEY_INDICES = {
    _BUTTON_X: INDEX_BUTTON_X,
    _BUTTON_Y: INDEX_BUTTON_Y,
    _BUTTON_B: INDEX_BUTTON_B,
    _BUTTON_A: INDEX_BUTTON_A,
    _BUTTON_RB: INDEX_BUTTON_RB,
    _BUTTON_LB: INDEX_BUTTON_LB,
}


def connected_devices() -> list[joystick_evdev.InputDevice]:
  return joystick_evdev.connected_devices(_F710_DEVICE_NAME_FILTER)


class LogitechF710State:
  """The current state of the joystick buttons and axes."""

  def __init__(self, joystick_state: joystick_evdev.JoystickState):
    self._buttons = copy.deepcopy(joystick_state.buttons)
    raw_axis_position = copy.deepcopy(joystick_state.axis_position)

    self._axis_position = [0.0] * len(_AXIS_REMAPPING)
    # Convert the axis position to the range [-1, 1].
    for index, raw_value in enumerate(raw_axis_position):
      value = raw_value / _MAX_JOYSTICK_VALUE
      self._axis_position[index] = _AXIS_INVERT[index] * value

  @classmethod
  def make_zero_state(cls) -> 'LogitechF710State':
    return cls(
        joystick_evdev.JoystickState(
            [0] * len(_KEY_INDICES), [0.0] * len(_AXIS_REMAPPING)
        )
    )

  @property
  def buttons(self) -> list[int]:
    return self._buttons

  @property
  def axis_position(self) -> list[float]:
    return self._axis_position

  @axis_position.setter
  def axis_position(self, value: list[float]):
    self._axis_position = value

  def __str__(self):
    return 'pos: {}, buttons: {}'.format(
        ','.join([str(x) for x in self.axis_position]),
        ','.join([str(x) for x in self.buttons]),
    )


class LogitechF710Interface:
  """An interface to a Logitech F710 device."""

  def __init__(
      self,
      device: joystick_evdev.InputDevice,
      enable_double_click: bool = False,
      timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
  ):
    init_state = joystick_evdev.JoystickState(
        [0] * len(_KEY_INDICES), [0.0] * len(_AXIS_REMAPPING)
    )
    self._joystick = joystick_evdev.JoystickEvdev(
        device=device,
        button_indices=_KEY_INDICES,
        axis_remapping=_AXIS_REMAPPING,
        enable_double_click=enable_double_click,
        timeout_seconds=timeout_seconds,
        init_state=init_state,
    )

  def close(self) -> None:
    self._joystick.close()

  def state(self) -> LogitechF710State:
    return LogitechF710State(self._joystick.state())

  def is_update_thread_alive(self) -> bool:
    return self._joystick.is_update_thread_alive()

  def get_update_thread_exception(self) -> Exception | None:
    return self._joystick.get_update_thread_exception()
