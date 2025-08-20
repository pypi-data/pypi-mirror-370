"""Tests for the settings module"""

import os
from typing import Type

import pytest

from dkist_service_configuration import ConfigurationBase
from dkist_service_configuration import MeshServiceConfigurationBase
from dkist_service_configuration.settings import DEFAULT_MESH_SERVICE
from dkist_service_configuration.settings import InstrumentedMeshServiceConfigurationBase


@pytest.fixture()
def environment_vars() -> dict:
    os.environ["foo"] = "1"
    os.environ["bar"] = "2"
    os.environ["LOGURU_LEVEL"] = "WARNING"
    os.environ[
        "MESH_CONFIG"
    ] = """{
    "upstream_service_name": {
        "mesh_address": "localhost",
        "mesh_port": 6742
    },
    "otlp_traces_endpoint": {"mesh_address": "127.0.0.1", "mesh_port": 4317},
    "otlp_metrics_endpoint": {"mesh_address": "127.0.0.1", "mesh_port": 4317}
}"""
    return dict(os.environ)


@pytest.fixture()
def base_config() -> Type[ConfigurationBase]:
    class BaseConfig(ConfigurationBase):
        foo: str

    return BaseConfig


def test_base_config(environment_vars, base_config):
    config = base_config()
    assert config.log_level == "WARNING"
    config.log_configurations()
    table = config.model_fields_to_markdown_table()
    print(table)


@pytest.fixture()
def mesh_config() -> Type[MeshServiceConfigurationBase]:
    class MeshConfig(MeshServiceConfigurationBase):
        bar: str = "foo"
        password: str = "bar"

    return MeshConfig


def test_mesh_config(environment_vars, mesh_config):
    config = mesh_config()
    assert config.log_level == "WARNING"
    assert config.service_mesh_detail("upstream_service_name").host == "localhost"
    assert config.service_mesh_detail("upstream_service_name").port == 6742
    config.log_configurations()


def test_default_mesh_config(environment_vars, mesh_config):
    config = mesh_config()
    assert config.service_mesh_detail("not_a_configured_service").host == DEFAULT_MESH_SERVICE.host
    assert config.service_mesh_detail("not_a_configured_service").port == DEFAULT_MESH_SERVICE.port


def test_instrumented_mesh_service_configuration_tracer(instrumented_mesh_config):
    """
    Given an instrumented mesh service configuration
    When the tracer is initialized
    Then the tracer should be set up correctly
    """
    tracer = instrumented_mesh_config.tracer
    with tracer.start_as_current_span(
        name="test_instrumented_mesh_service_configuration_tracer"
    ) as span:
        pass


def test_instrumented_mesh_service_configuration_meter(instrumented_mesh_config):
    """
    Given an instrumented mesh service configuration
    When the meter is initialized
    Then the meter should be set up correctly
    """
    meter = instrumented_mesh_config.meter
    counter = meter.create_up_down_counter(
        name="test_instrumented_mesh_service_configuration_meter",
        unit="1",
        description="The number of times this counter is incremented",
    )
    counter.add(1)


def test_auto_instrument(instrumented_mesh_config):
    """
    Given an instrumented mesh service configuration
    When the auto_instrument method is called
    Then the tracer and meter should be set up correctly
    """
    instrumented_mesh_config.auto_instrument()
    assert instrumented_mesh_config.tracer is not None
    assert instrumented_mesh_config.meter is not None
