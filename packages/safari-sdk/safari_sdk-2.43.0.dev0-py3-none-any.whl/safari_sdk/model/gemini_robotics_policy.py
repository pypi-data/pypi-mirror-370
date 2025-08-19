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

"""Gemini Robotics Policy."""

from collections.abc import Iterable
from concurrent import futures
import copy
import enum
import json
import logging
import threading
from typing import Any

import dm_env
from dm_env import specs
from gdm_robotics.interfaces import policy as gdmr_policy
from gdm_robotics.interfaces import types as gdmr_types
import numpy as np
import tensorflow as tf
import tree
from typing_extensions import override

from safari_sdk.model import genai_robotics

_IMAGE_ENCODED_OBS_PREFIX = 'images/'
_CONDITIONING_ENCODED_OBS_KEY = 'conditioning'
_TASK_INSTRUCTION_ENCODED_OBS_KEY = 'task_instruction'


class InferenceMode(enum.Enum):
  SYNCHRONOUS = enum.auto()
  ASYNCHRONOUS = enum.auto()


class GeminiRoboticsPolicy(gdmr_policy.Policy[np.ndarray]):
  """Policy which uses the Gemini Robotics API."""

  def __init__(
      self,
      serve_id: str,
      task_instruction_key: str,
      image_observation_keys: Iterable[str],
      proprioceptive_observation_keys: Iterable[str],
      min_replan_interval: int = 15,
      inference_mode: InferenceMode = InferenceMode.ASYNCHRONOUS,
      robotics_api_connection: genai_robotics.RoboticsApiConnectionType = genai_robotics.RoboticsApiConnectionType.CLOUD,
  ):
    """Initializes the evaluation policy.

    Note: this is policy has an implicit state which is not returned by the
    functions.

    Important: Before using the policy (i.e. calling `initial_state` and `step`)
    you must initialize it by providing the timestep spec by calling
    `step_spec`.

    Args:
      serve_id: The serve ID to use for the policy.
      task_instruction_key: The key of the task instruction in the observation.
      image_observation_keys: A list of observation keys that are related to
        images.
      proprioceptive_observation_keys: The list of observation keys that are
        related to proprioceptive sensors (e.g. joints).
      min_replan_interval: The minimum number of steps to wait before replanning
        the task instruction.
      inference_mode: Whether to use an async or sync implementation of the
        policy.
      robotics_api_connection: Connection type for the Robotics API.
    """
    self._serve_id = serve_id
    self._task_instruction_key = task_instruction_key
    self._image_observation_keys = list(image_observation_keys)
    self._proprioceptive_observation_keys = list(
        proprioceptive_observation_keys
    )
    self._min_replan_interval = min_replan_interval

    self._dummy_state = np.zeros(())

    self._model_output = np.array([])
    self._action_spec: gdmr_types.UnboundedArraySpec | None = None
    self._timestep_spec: gdmr_types.TimeStepSpec | None = None
    self._num_of_actions_per_request = 0

    # Initialize the genai_robotics client
    self._client = genai_robotics.Client(
        use_robotics_api=True,  # Use the specific Robotics API endpoint
        robotics_api_connection=robotics_api_connection,
    )
    # Threading setup
    self._inference_mode = inference_mode
    if inference_mode == InferenceMode.ASYNCHRONOUS:
      self._executor = futures.ThreadPoolExecutor(max_workers=1)
      self._future: futures.Future[np.ndarray] | None = None
      self._model_output_lock = threading.Lock()
      self._actions_executed_during_inference = 0

  @override
  def initial_state(
      self,
  ) -> gdmr_types.StateStructure[np.ndarray]:
    """Resets the policy and returns the policy initial state."""
    if self._action_spec is None:
      raise ValueError('Cannot call initial_state before calling step_spec.')

    if self._inference_mode == InferenceMode.ASYNCHRONOUS:
      # Cancel any pending futures on reset
      if self._future and self._future.running():
        self._future.cancel()
      self._future = None

    self._model_output = np.array([])

    return self._dummy_state

  @override
  def step(
      self,
      timestep: dm_env.TimeStep,
      prev_state: gdmr_types.StateStructure[np.ndarray],
  ) -> tuple[
      tuple[
          gdmr_types.ActionType,
          gdmr_types.ExtraOutputStructure[np.ndarray],
      ],
      gdmr_types.StateStructure[np.ndarray],
  ]:
    """Takes a step with the policy given an environment timestep.

    Args:
      timestep: An instance of environment `TimeStep`.
      prev_state: This is ignored.

    Returns:
      A tuple of ((action, extra), state) with `action` indicating the action to
      be executed, extra an empty dict and state the dummy policy state.
    """
    del prev_state  # Unused.

    if self._inference_mode == InferenceMode.ASYNCHRONOUS:
      action = self._step_async(timestep.observation)
    else:
      action = self._step_sync(timestep.observation)

    return (action, {}), self._dummy_state

  @override
  def step_spec(self, timestep_spec: gdmr_types.TimeStepSpec) -> tuple[
      tuple[gdmr_types.ActionSpec, gdmr_types.ExtraOutputSpec],
      gdmr_types.StateSpec,
  ]:
    """Returns the spec of the ((action, extra), state) from `step` method."""
    self._timestep_spec = timestep_spec

    # Validate that the timestep_spec contains the required keys.
    if self._task_instruction_key not in timestep_spec.observation:
      raise ValueError(
          f'timestep_spec does not contain {self._task_instruction_key}.'
      )

    if self._image_observation_keys and not all(
        image_obs_key in timestep_spec.observation
        for image_obs_key in self._image_observation_keys
    ):
      raise ValueError(
          'timestep_spec does not contain all image observation keys.'
          f' Expected: {self._image_observation_keys}, actual:'
          f' {timestep_spec.observation}'
      )
    if self._proprioceptive_observation_keys and not all(
        proprio_obs_key in timestep_spec.observation
        for proprio_obs_key in self._proprioceptive_observation_keys
    ):
      raise ValueError(
          'timestep_spec does not contain all proprioceptive observation keys.'
          f' Expected: {self._proprioceptive_observation_keys}, actual:'
          f' {timestep_spec.observation}'
      )

    if self._action_spec is None:
      logging.warning('action_spec is None, initializing policy.')
      self._setup()
    if self._action_spec is None:
      raise ValueError('action_spec is None, setup failed')

    return (self._action_spec, {}), specs.Array(shape=(), dtype=np.float32)

  def _setup(self):
    """Initializes the policy."""
    if self._timestep_spec is None:
      raise ValueError('timestep_spec is None. Call step_spec first.')

    empty_observation = tree.map_structure(
        lambda s: s.generate_value(), self._timestep_spec.observation
    )
    # Instruction observations cannot be empty.
    empty_observation[self._task_instruction_key] = np.array(
        'dummy instruction'
    )

    self._actions_buffer = self._query_model(empty_observation, np.array([]))
    # First axis is the number of actions.
    self._num_of_actions_per_request = self._actions_buffer.shape[0]

    self._action_spec = gdmr_types.UnboundedArraySpec(
        shape=self._actions_buffer.shape[1:],
        dtype=np.float32,
    )

  def _should_replan(self) -> bool:
    """Returns whether the policy should replan."""
    assert self._action_spec is not None
    actions_left = self._model_output.shape[0]
    if (
        self._num_of_actions_per_request - actions_left
    ) >= self._min_replan_interval:
      return True
    if actions_left == 0:
      return True
    return False

  def _step_sync(self, observation: dict[str, np.ndarray]) -> np.ndarray:
    """Computes an action from observations."""
    if self._should_replan():
      self._model_output = self._query_model(observation, self._model_output)
      assert self._model_output.shape[0] > 0

    action = self._model_output[0]
    self._model_output = self._model_output[1:]
    return action

  def _step_async(self, observation: dict[str, np.ndarray]) -> np.ndarray:
    """Computes an action from the given observation.

    Method:
    1. If Gemini Returned an action chunk, update the action buffer.
    2. If no Gemini query is pending and the action buffer is less than the
       minimum replan interval, trigger a new query.
    3. If the action buffer is empty (first query) trigger a new query.
    4. If there is more than one action in the buffer, consume the first
       action and remove it from the buffer.
    5. If only one action is in the buffer, consume it without removing it (we
    will keep outputting this action until a new action is generated, this is an
    edge case that should not happen in practice). This results in a quasi-async
    implementation.

    Args:
        observation: A dictionary of observations from the environment.

    Returns:
        The next action to take.

    Raises:
        ValueError: If no actions are available and no future to generate them
        is present.
    """
    with self._model_output_lock:
      # If new model output is available, update the buffer.
      if self._future and self._future.done():
        new_model_output = self._future.result()
        # Remove the actions that were executed while the future was running.
        self._model_output = new_model_output[
            self._actions_executed_during_inference :
        ]
        self._future = None
      actions_left = self._model_output.shape[0]

      # If not enough actions left and not generating, trigger a replan.
      if self._should_replan() and self._future is None:
        self._future = self._executor.submit(
            self._query_model,
            copy.deepcopy(observation),
            copy.deepcopy(self._model_output),
        )
        self._actions_executed_during_inference = 0

    # If no actions left (first query), block until the future is done.
    if actions_left == 0:
      if not self._future:
        raise ValueError('No actions left and no future to generate them.')
      result_from_blocking_wait = self._future.result()
      with self._model_output_lock:
        self._model_output = result_from_blocking_wait[
            self._actions_executed_during_inference :
        ]
        self._future = None

    # Consume the action.
    with self._model_output_lock:
      action = self._model_output[0]
      self._model_output = self._model_output[1:]
      self._actions_executed_during_inference += 1
    return action

  def _observation_to_contents(
      self,
      observation: dict[str, np.ndarray],
      model_output: np.ndarray,
  ) -> list[Any]:
    """Encodes the observation as a GenerateRequest."""
    encoded_observation = {}
    # Conditioning on what the model has left to output.
    if (
        self._inference_mode == InferenceMode.ASYNCHRONOUS
        and model_output.size > 0
    ):
      encoded_observation[_CONDITIONING_ENCODED_OBS_KEY] = model_output.tolist()

    # Encode the task instruction as plain string.
    plain_str = np.array_str(observation[self._task_instruction_key])
    encoded_observation[_TASK_INSTRUCTION_ENCODED_OBS_KEY] = plain_str

    for obs_name in self._proprioceptive_observation_keys:
      proprio_obs = observation[obs_name]
      # Tolerate common mistake of having an extra batch dimension.
      if proprio_obs.ndim == 2:
        proprio_obs = proprio_obs[0]
      if proprio_obs.ndim != 1:
        raise ValueError(
            f'Observation {obs_name} has {proprio_obs.ndim} dimensions, but'
            ' should be 1.'
        )
      encoded_observation[obs_name] = proprio_obs.tolist()

    images = []
    for i, image_obs_name in enumerate(self._image_observation_keys):
      encoded_observation[f'{_IMAGE_ENCODED_OBS_PREFIX}{image_obs_name}'] = i
      image = observation[image_obs_name]
      if isinstance(image, (np.ndarray, tf.Tensor)):
        # Tolerate common mistake of having an extra batch dimension.
        image_dim = image.ndim
        if image_dim == 4:
          image = image[0]
        if image.ndim != 3:
          raise ValueError(
              f'Image {image_obs_name} has {image_dim} dimensions, but should'
              ' be 3.'
          )
      elif isinstance(image, bytes):
        pass  # can directly take encoded image bytes.
      else:
        raise ValueError(
            f'Image {image_obs_name} is of type {type(image)}, but should be'
            ' np.ndarray, tf.Tensor or bytes.'
        )
      images.append(image)
    return [
        *images,
        json.dumps(encoded_observation),
    ]

  def _query_model(
      self,
      observation: dict[str, np.ndarray],
      model_output: np.ndarray,
  ) -> np.ndarray:
    """Queries the model with the given observation and task instruction."""
    contents = self._observation_to_contents(observation, model_output)

    response = self._client.models.generate_content(
        model=self._serve_id,
        contents=contents,
    )

    # Parse the response text (assuming its JSON containing the action)
    response_data = json.loads(response.text)
    # Assuming the structure is {'action_chunk': [...]}
    action_chunk = response_data.get('action_chunk')
    if action_chunk is None:
      raise ValueError("Response JSON does not contain 'action_chunk'")
    return np.array(action_chunk)

  @property
  def policy_type(self) -> str:
    if self._inference_mode == InferenceMode.ASYNCHRONOUS:
      return f'gemini_robotics_async[{self._serve_id}]'
    return f'gemini_robotics[{self._serve_id}]'
