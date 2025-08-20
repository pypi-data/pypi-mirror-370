"""
Wrapper for retrieving configurations and safely logging their retrieval
"""

import logging
import re
from datetime import datetime
from functools import cached_property
from importlib.metadata import version
from uuid import uuid4

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.metrics import Meter
from opentelemetry.metrics import NoOpMeterProvider
from opentelemetry.metrics import get_meter
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import NoOpTracerProvider
from opentelemetry.trace import StatusCode
from opentelemetry.trace import Tracer
from opentelemetry.trace import get_tracer
from opentelemetry.trace import set_tracer_provider
from pydantic import BaseModel
from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from dkist_service_configuration.retryer import RetryConfig

logger = logging.getLogger(__name__)


class ConfigurationBase(BaseSettings):
    """Settings base which logs configured settings while censoring secrets"""

    log_level: str = Field(
        default="INFO", validation_alias="LOGURU_LEVEL", description="Log level for the application"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @staticmethod
    def _is_secret(field_name: str) -> bool:
        for pattern in ("pass", "secret", "token"):
            if re.search(pattern, field_name):
                return True
        return False

    def log_configurations(self):
        for field_name in self.model_fields:
            if self._is_secret(field_name=field_name):
                logger.info(f"{field_name}: <CENSORED>")
            else:
                logger.info(f"{field_name}: {getattr(self, field_name)}")

    def model_fields_to_markdown_table(self):
        rows = []
        for field, field_info in self.model_fields.items():
            if isinstance(field_info, FieldInfo) and field_info.validation_alias is not None:
                environment_variable = field_info.validation_alias
            else:
                environment_variable = field.upper()
            description = str(field_info)
            rows.append((environment_variable, description))

        # Determine max widths
        max_environment_variable_len = max(len(var) for var, _ in rows)
        max_description_len = max(len(desc) for _, desc in rows)

        # Create header and separator with padding
        header = f"| {'Environment Variable'.ljust(max_environment_variable_len)} | {'FieldInfo'.ljust(max_description_len)} |"
        separator = (
            f"|{'-' * (max_environment_variable_len + 2)}|{'-' * (max_description_len + 2)}|"
        )

        # Format all rows
        table = [header, separator]
        for environment_variable, field in rows:
            table.append(
                f"| {environment_variable.ljust(max_environment_variable_len)} | {field.ljust(max_description_len)} |"
            )

        return "\n".join(table)


class MeshService(BaseModel):
    """Model of the metadata for a node in the service mesh"""

    host: str = Field(default=..., alias="mesh_address")
    port: int = Field(default=..., alias="mesh_port")


DEFAULT_MESH_SERVICE = MeshService(mesh_address="127.0.0.1", mesh_port=0)


class MeshServiceConfigurationBase(ConfigurationBase):
    """
    Settings base for services using a mesh configuration to define connections in the form
    {
        "upstream_service_name": {"mesh_address": "localhost", "mesh_port": 6742}
    }
    """

    service_mesh: dict[str, MeshService] = Field(
        default_factory=dict,
        validation_alias="MESH_CONFIG",
        description="Service mesh configuration",
        examples=[{"upstream_service_name": {"mesh_address": "localhost", "mesh_port": 6742}}],
    )
    retry_config: RetryConfig = Field(
        default_factory=RetryConfig, description="Retry configuration for the service"
    )

    def service_mesh_detail(
        self, service_name: str, default_mesh_service: MeshService = DEFAULT_MESH_SERVICE
    ) -> MeshService:
        mesh_service = self.service_mesh.get(service_name) or default_mesh_service
        return mesh_service


class InstrumentedMeshServiceConfigurationBase(MeshServiceConfigurationBase):
    service_name: str = Field(
        default="unknown-service-name",
        validation_alias="OTEL_SERVICE_NAME",
        description="Service name for OpenTelemetry",
    )
    service_version: str = Field(
        default="unknown-service-version",
        validation_alias="DKIST_SERVICE_VERSION",
        description="Service version for OpenTelemetry",
    )
    allocation_id: str = Field(
        default="unknown-allocation-id",
        validation_alias="NOMAD_ALLOC_ID",
        description="Nomad allocation ID for OpenTelemetry",
    )
    # OpenTelemetry configurations
    otel_exporter_otlp_traces_insecure: bool = Field(
        default=True, description="Use insecure connection for OTLP traces"
    )
    otel_exporter_otlp_metrics_insecure: bool = Field(
        default=True, description="Use insecure connection for OTLP metrics"
    )
    otel_exporter_otlp_traces_endpoint: str | None = Field(
        default=None,
        description="OTLP traces endpoint. Overrides mesh configuration",
        examples=["localhost:4317"],
    )
    otel_exporter_otlp_metrics_endpoint: str | None = Field(
        default=None,
        description="OTLP metrics endpoint. Overrides mesh configuration",
        examples=["localhost:4317"],
    )
    otel_python_disabled_instrumentations: list[str] = Field(
        default_factory=list,
        description="List of instrumentations to disable. https://opentelemetry.io/docs/zero-code/python/configuration/",
        examples=[
            ["pika", "requests"],
        ],
    )
    otel_python_fastapi_excluded_urls: str = Field(
        default=r"health",
        description="Comma separated list of URLs to exclude from OpenTelemetry instrumentation in FastAPI.",
        examples=[
            r"client/.*/info,healthcheck",
        ],
    )
    system_metric_instrumentation_config: dict[str, bool] | None = Field(
        default=None,
        description="Configuration for system metric instrumentation. https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/system_metrics/system_metrics.html",
        examples=[
            {
                "system.memory.usage": ["used", "free", "cached"],
                "system.cpu.time": ["idle", "user", "system", "irq"],
                "system.network.io": ["transmit", "receive"],
                "process.runtime.memory": ["rss", "vms"],
                "process.runtime.cpu.time": ["user", "system"],
                "process.runtime.context_switches": ["involuntary", "voluntary"],
            },
        ],
    )

    @property
    def otel_meter_name(self) -> str:
        return "dkist"

    @property
    def otlp_traces_endpoint(self) -> str | None:
        if self.otel_exporter_otlp_traces_endpoint:
            return self.otel_exporter_otlp_traces_endpoint  # allow environment var to override

        service_info = self.service_mesh_detail(service_name="otlp-traces-endpoint")
        if service_info == DEFAULT_MESH_SERVICE:
            return None  # Not configured
        return f"{service_info.host}:{service_info.port}"  # mesh definition

    @property
    def otlp_metrics_endpoint(self) -> str | None:
        if self.otel_exporter_otlp_metrics_endpoint:
            return self.otel_exporter_otlp_traces_endpoint  # allow environment var to override

        service_info = self.service_mesh_detail(service_name="otlp-metrics-endpoint")
        if service_info == DEFAULT_MESH_SERVICE:
            return None  # Not configured
        return f"{service_info.host}:{service_info.port}"  # mesh definition

    @property
    def otel_resource(self) -> Resource:
        return Resource(
            attributes={
                "service.name": self.service_name,
                "service.instance.id": self.allocation_id,
                "service.version": self.service_version,
            }
        )

    @cached_property
    def tracer(self) -> Tracer:
        if self.otlp_traces_endpoint is not None:
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.otlp_traces_endpoint,
                insecure=self.otel_exporter_otlp_traces_insecure,
            )
            tracer_provider = TracerProvider(resource=self.otel_resource)
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor=span_processor)
        else:
            tracer_provider = NoOpTracerProvider()

        # register global tracer provider
        set_tracer_provider(tracer_provider=tracer_provider)
        # get tracer
        instrumenting_module_name = "dkist_service_configuration"
        instrumenting_library_version = version(instrumenting_module_name)
        tracer = get_tracer(
            instrumenting_module_name=instrumenting_module_name,
            instrumenting_library_version=instrumenting_library_version,
        )

        return tracer

    @cached_property
    def meter(self) -> Meter:
        if self.otlp_metrics_endpoint is not None:
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(
                    endpoint=self.otlp_metrics_endpoint,
                    insecure=self.otel_exporter_otlp_metrics_insecure,
                )
            )
            meter_provider = MeterProvider(
                metric_readers=[metric_reader], resource=self.otel_resource
            )
        else:
            meter_provider = NoOpMeterProvider()
        # register global meter provider
        set_meter_provider(meter_provider)
        # get meter
        meter = get_meter(
            name=self.otel_meter_name,
            version=version("dkist_service_configuration"),
            meter_provider=meter_provider,
        )
        return meter

    def auto_instrument(self):
        """
        Install all available instrumentors.
        To disable any instrumentor, set the environment variable
        `OTEL_PYTHON_DISABLED_INSTRUMENTATIONS` to a comma separated list of instrumentor names. e.g.:
            export OTEL_PYTHON_DISABLED_INSTRUMENTATIONS=["pika","requests","psycopg2","pymongo" ]
        """
        # Ensure provider registration
        _ = self.tracer
        _ = self.meter

        # Check if the auto instrumentation is disabled via settings in order to
        # support .env configuration
        if "pika" not in self.otel_python_disabled_instrumentations:
            try:
                from opentelemetry.instrumentation.pika import PikaInstrumentor

                PikaInstrumentor().instrument()
            except ImportError as e:  # pragma: no cover
                logger.info(
                    f"PikaInstrumentor failed instrumentation {e=}. Skipping."
                )  # pragma: no cover
        if "requests" not in self.otel_python_disabled_instrumentations:
            try:
                from opentelemetry.instrumentation.requests import RequestsInstrumentor

                RequestsInstrumentor().instrument()
            except ImportError as e:  # pragma: no cover
                logger.info(
                    f"RequestsInstrumentor failed instrumentation {e=}. Skipping."
                )  # pragma: no cover
        if "aiohttp" not in self.otel_python_disabled_instrumentations:
            try:
                from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor

                AioHttpClientInstrumentor().instrument()  # pragma: no cover
            except ImportError as e:
                logger.info(f"AioHttpClientInstrumentor failed instrumentation {e=}. Skipping.")
        if "botocore" not in self.otel_python_disabled_instrumentations:
            try:
                from opentelemetry.instrumentation.botocore import BotocoreInstrumentor

                BotocoreInstrumentor().instrument()  # pragma: no cover
            except ImportError as e:
                logger.info(f"BotocoreInstrumentor failed instrumentation {e=}. Skipping.")
        if "celery" not in self.otel_python_disabled_instrumentations:
            try:
                from opentelemetry.instrumentation.celery import CeleryInstrumentor

                CeleryInstrumentor().instrument()  # pragma: no cover
            except ImportError as e:
                logger.info(f"CeleryInstrumentor failed instrumentation {e=}. Skipping.")
        if "psycopg2" not in self.otel_python_disabled_instrumentations:
            try:
                from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

                Psycopg2Instrumentor().instrument()  # pragma: no cover
            except ImportError as e:
                logger.info(f"Psycopg2Instrumentor failed instrumentation {e=}. Skipping.")
        if "pymongo" not in self.otel_python_disabled_instrumentations:
            try:
                from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

                PymongoInstrumentor().instrument()  # pragma: no cover
            except ImportError as e:
                logger.info(f"PymongoInstrumentor failed instrumentation {e=}. Skipping.")
        if "redis" not in self.otel_python_disabled_instrumentations:
            try:
                from opentelemetry.instrumentation.redis import RedisInstrumentor

                RedisInstrumentor().instrument()  # pragma: no cover
            except ImportError as e:
                logger.info(f"RedisInstrumentor failed instrumentation {e=}. Skipping.")
        if "sqlalchemy" not in self.otel_python_disabled_instrumentations:
            try:
                from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

                SQLAlchemyInstrumentor().instrument()  # pragma: no cover
            except ImportError as e:
                logger.info(f"SQLAlchemyInstrumentor failed instrumentation {e=}. Skipping.")
        if "system_metrics" not in self.otel_python_disabled_instrumentations:
            # installed with deps as part of the dkist_service_configuration
            from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor

            SystemMetricsInstrumentor(config=self.system_metric_instrumentation_config).instrument()

    def _auto_instrument_fastapi(self, app):
        """
        Instrument FastAPI application with OpenTelemetry.
        """
        if "fastapi" not in self.otel_python_disabled_instrumentations:
            # only attempt imports if fast api instrumentation is not disabled
            from dkist_service_configuration.middleware import instrument_fastapi_app

            instrument_fastapi_app(app=app, excluded_urls=self.otel_python_fastapi_excluded_urls)

    def add_fastapi_middleware(self, app):
        """Add DKIST middleware to FastAPI application."""

        # auto instrument the FastAPI app
        self._auto_instrument_fastapi(app=app)

        # add the DKIST middleware to the FastAPI app
        from dkist_service_configuration.middleware import add_dkist_middleware

        add_dkist_middleware(
            app=app,
            tracer=self.tracer,
            meter=self.meter,
            excluded_urls=self.otel_python_fastapi_excluded_urls,
        )
