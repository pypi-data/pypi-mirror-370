from google.protobuf import struct_pb2
from absl.testing import absltest
from safari_sdk.logging.python import session_manager
from safari_sdk.protos import label_pb2

_TEST_TASK_ID = "test_task"


class SessionManagerTest(absltest.TestCase):

  def test_init_with_valid_inputs(self):
    manager = session_manager.SessionManager(
        topics={"topic1", "topic2", "topic3"},
        required_topics={"topic1", "topic2"},
    )
    self.assertEqual(manager._topics, {"topic1", "topic2", "topic3"})
    self.assertEqual(manager._required_topics, {"topic1", "topic2"})
    self.assertFalse(manager.session_started)

  def test_init_with_invalid_required_topics(self):
    with self.assertRaisesRegex(
        ValueError, "required_topics must be a subset of topics"
    ):
      session_manager.SessionManager(
          topics={"topic1", "topic2"},
          required_topics={"topic1", "topic3"},
      )

  def test_start_session(self):
    manager = session_manager.SessionManager(
        topics={"topic1", "topic2", "topic3"},
        required_topics={"topic1", "topic2"},
    )
    start_nsec = 1234567890
    task_id = _TEST_TASK_ID
    manager.start_session(start_timestamp_nsec=start_nsec, task_id=task_id)
    self.assertTrue(manager.session_started)
    self.assertEqual(manager._session.interval.start_nsec, start_nsec)
    self.assertEqual(manager._session.task_id, _TEST_TASK_ID)
    self.assertLen(manager._session.streams, 3)
    for stream in manager._session.streams:
      self.assertEqual(stream.key_range.interval.start_nsec, start_nsec)
      self.assertEqual(
          stream.is_required, stream.key_range.topic in ["topic1", "topic2"]
      )

  def test_start_session_twice_raises_error(self):
    manager = session_manager.SessionManager(
        topics={"topic1", "topic2"},
        required_topics={"topic1"},
    )
    manager.start_session(start_timestamp_nsec=123, task_id=_TEST_TASK_ID)
    with self.assertRaisesRegex(ValueError, "Session has already been started"):
      manager.start_session(start_timestamp_nsec=456, task_id="test_task2")

  def test_add_session_label(self):
    manager = session_manager.SessionManager(
        topics={"topic1", "topic2"},
        required_topics={"topic1"},
    )
    manager.start_session(start_timestamp_nsec=123, task_id=_TEST_TASK_ID)
    label1 = label_pb2.LabelMessage(
        key="key1", label_value=struct_pb2.Value(string_value="value1")
    )
    label2 = label_pb2.LabelMessage(
        key="key2", label_value=struct_pb2.Value(string_value="value2")
    )
    manager.add_session_label(label1)
    manager.add_session_label(label2)
    self.assertLen(manager._session.labels, 2)
    self.assertEqual(manager._session.labels[0], label1)
    self.assertEqual(manager._session.labels[1], label2)

  def test_add_session_label_before_start_raises_error(self):
    manager = session_manager.SessionManager(
        topics={"topic1", "topic2"},
        required_topics={"topic1"},
    )
    label = label_pb2.LabelMessage(
        key="key1", label_value=struct_pb2.Value(string_value="value1")
    )
    with self.assertRaisesRegex(
        ValueError,
        "add_session_label is called before session has been started",
    ):
      manager.add_session_label(label)

  def test_stop_session(self):
    manager = session_manager.SessionManager(
        topics={"topic1", "topic2"},
        required_topics={"topic1"},
    )
    start_nsec = 123
    stop_nsec = 456
    manager.start_session(
        start_timestamp_nsec=start_nsec, task_id=_TEST_TASK_ID
    )
    session = manager.stop_session(stop_timestamp_nsec=stop_nsec)

    self.assertFalse(manager.session_started)
    self.assertEqual(session.interval.stop_nsec, stop_nsec)
    for stream in session.streams:
      self.assertEqual(stream.key_range.interval.stop_nsec, stop_nsec)

  def test_stop_session_before_start_raises_error(self):
    manager = session_manager.SessionManager(
        topics={"topic1", "topic2"},
        required_topics={"topic1"},
    )
    with self.assertRaisesRegex(ValueError, "Session is not started"):
      manager.stop_session(stop_timestamp_nsec=456)


if __name__ == "__main__":
  absltest.main()
