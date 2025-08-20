"""Common MessageProcessor classes for the Interservice Bus."""

from abc import ABC
from functools import partial

import pika
from opentelemetry.metrics import Meter
from opentelemetry.metrics import NoOpMeter
from opentelemetry.metrics import UpDownCounter
from opentelemetry.trace import NoOpTracer
from opentelemetry.trace import StatusCode
from opentelemetry.trace import Tracer
from pydantic import Field
from talus import ConsumeMessageBase
from talus import MessageProcessorBase


class InstrumentedMessageProcessorBase(MessageProcessorBase, ABC):
    """
    Message processor base class with open telemetry instrumentation.
    """

    tracer: Tracer = Field(default_factory=NoOpTracer)
    meter: Meter = Field(default_factory=partial(NoOpMeter, name="NoOpMeter"))

    def format_metric_name(self, name: str) -> str:
        """
        Format the metric name to include the meter name.  Words are separated by a dot.
        For example, if the meter name is "service.meter" and the metric name is "message.received",
        the formatted name will be "service.meter.message.received".
        """
        return f"{self.meter.name}.isb.{name}"

    @property
    def received_message_counter(self) -> UpDownCounter:

        return self.meter.create_up_down_counter(
            name=self.format_metric_name("message.received"),
            unit="1",
            description="The number of messages received",
        )

    @property
    def acknowledged_message_counter(self) -> UpDownCounter:
        return self.meter.create_up_down_counter(
            name=self.format_metric_name("message.acknowledged"),
            unit="1",
            description="The number of messaged acknowledged",
        )

    @property
    def dlq_message_counter(self) -> UpDownCounter:
        return self.meter.create_up_down_counter(
            name=self.format_metric_name("message.dlq"),
            unit="1",
            description="The number of messaged sent to the DLQ",
        )

    def acknowledge_message(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        message: ConsumeMessageBase,
    ) -> None:
        self.acknowledged_message_counter.add(1)
        with self.tracer.start_as_current_span("Acknowledge Message") as span:
            super().acknowledge_message(channel, message)
            span.set_status(StatusCode.OK)

    def dlq_message(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        exception: Exception | None = None,
    ) -> None:
        self.dlq_message_counter.add(1)
        with self.tracer.start_as_current_span("DLQ Message") as span:
            super().dlq_message(channel, method, properties, exception)
            span.set_status(StatusCode.ERROR)
            span.record_exception(exception)

    def __call__(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ) -> "InstrumentedMessageProcessorBase":
        """
        Process the transfer success message inside a Trace
        """
        transaction_name = f"Process {method.routing_key} Message"
        self.received_message_counter.add(1)
        with self.tracer.start_as_current_span(name=transaction_name) as span:
            try:
                result = super().__call__(channel, method, properties, body)
                span.set_status(StatusCode.OK)
                return result
            except Exception as e:
                span.set_status(StatusCode.ERROR)
                span.record_exception(e)
                raise e
