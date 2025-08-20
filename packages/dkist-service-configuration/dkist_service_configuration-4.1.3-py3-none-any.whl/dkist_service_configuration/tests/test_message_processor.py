"""Unit tests for the message_processor module."""

from unittest.mock import MagicMock

import pika
import pytest
from talus import ConsumeMessageBase

from dkist_service_configuration.message_processor import InstrumentedMessageProcessorBase


@pytest.fixture()
def channel() -> pika.adapters.blocking_connection.BlockingChannel:
    return MagicMock(spec=pika.adapters.blocking_connection.BlockingChannel)


@pytest.fixture()
def properties() -> pika.spec.BasicProperties:
    return pika.spec.BasicProperties()


@pytest.fixture()
def method() -> pika.spec.Basic.Deliver:
    return pika.spec.Basic.Deliver(routing_key="test.m", delivery_tag="test")


@pytest.fixture()
def valid_body() -> dict:
    data = {
        "bucket": "inbox",
        "objectName": "bar",
    }
    return data


@pytest.fixture()
def message_processor_cls() -> InstrumentedMessageProcessorBase:
    class MessageProcessor(InstrumentedMessageProcessorBase):
        def process_message(self, message: ConsumeMessageBase):
            self._process_message_called = True

    return MessageProcessor


def test_message_processor_success(
    channel,
    method,
    properties,
    valid_body,
    message_processor_cls,
):
    """
    :given: A message processor that does not raise an exception.
    :when: The message processor is called.
    :then: The message processor should process and acknowledge the message.
    """
    # given
    message_processor = message_processor_cls()
    # when
    message_processor(channel=channel, method=method, properties=properties, body=valid_body)
    # then
    assert message_processor._process_message_called
    channel.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)


@pytest.fixture()
def invalid_body() -> str:
    return "not good, json {}"


def test_message_processor_handled_error(
    channel,
    method,
    properties,
    invalid_body,
    message_processor_cls,
):
    """
    :given: A message processor that raises an exception.
    :when: The message processor is called.
    :then: The message processor should process and reject the message.
    """
    # given
    message_processor = message_processor_cls()
    # when
    message_processor(channel=channel, method=method, properties=properties, body=invalid_body)
    # then
    channel.basic_nack.assert_called_once_with(delivery_tag=method.delivery_tag, requeue=False)


@pytest.fixture()
def erroring_message_processor_cls() -> InstrumentedMessageProcessorBase:
    class MessageProcessor(InstrumentedMessageProcessorBase):
        def process_message(self, message: ConsumeMessageBase):
            self._process_message_called = True
            raise RuntimeError("Error")

    return MessageProcessor


def test_message_processor_unhandled_error(
    channel,
    method,
    properties,
    valid_body,
    erroring_message_processor_cls,
):
    """
    :given: A message processor that does raise an exception.
    :when: The message processor is called.
    :then: The message processor should reraise the error.
    """
    # given
    message_processor = erroring_message_processor_cls()
    # when/then
    with pytest.raises(RuntimeError):
        message_processor(channel=channel, method=method, properties=properties, body=valid_body)
