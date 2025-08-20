"""Shared fixtures for pytest."""

import pytest

from dkist_service_configuration import InstrumentedMeshServiceConfigurationBase


@pytest.fixture(
    params=[
        pytest.param(
            "exporter_endpoint_from_env_var",
            marks=pytest.mark.skip(reason="need otlp endpoint to connect to"),
        ),
        pytest.param(
            "exporter_endpoint_from_mesh_config",
            marks=pytest.mark.skip(reason="need otlp endpoint to connect to"),
        ),
        None,
    ]
)
def instrumented_mesh_config(request):
    kwargs = {}
    if request.param == "exporter_endpoint_from_env_var":
        kwargs = {
            "otel_exporter_otlp_traces_endpoint": "localhost:4317",
            "otel_exporter_otlp_metrics_endpoint": "localhost:4317",
        }
    elif request.param == "exporter_endpoint_from_mesh_config":
        kwargs = {
            "MESH_CONFIG": {
                "otlp-traces-endpoint": {
                    "mesh_address": "localhost",
                    "mesh_port": 4317,
                },
                "otlp-metrics-endpoint": {
                    "mesh_address": "localhost",
                    "mesh_port": 4317,
                },
            }
        }
    config = InstrumentedMeshServiceConfigurationBase(**kwargs)
    return config
