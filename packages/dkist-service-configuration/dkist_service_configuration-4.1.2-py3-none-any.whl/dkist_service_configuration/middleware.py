"""Middleware for FastAPI applications"""

import logging
from datetime import datetime
from multiprocessing.managers import dispatch
from uuid import uuid4

from opentelemetry.metrics import Meter
from opentelemetry.trace import StatusCode
from opentelemetry.trace import Tracer
from opentelemetry.util.http import parse_excluded_urls
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


try:
    from fastapi import FastAPI
    from fastapi import Request
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from secure import Secure
except ImportError as e:  # pragma: no cover
    logger.error(
        f"Dependencies missing. Is the 'fastapi' extra installed? e.g. pip install -U dkist-service-configuration[fastapi]: {e}"
    )  # pragma: no cover
    raise e  # pragma: no cover


__all__ = ["add_dkist_middleware", "instrument_fastapi_app"]


MAX_METRIC_NAME_LENGTH = 62


def instrument_fastapi_app(app: FastAPI, excluded_urls: str | None = None) -> None:

    FastAPIInstrumentor().instrument_app(app=app, excluded_urls=excluded_urls)


def _parse_request_for_route(request: Request, max_length: int = MAX_METRIC_NAME_LENGTH) -> str:
    """
    Parse the request to extract the route name
    :param request: HTTP request object
    :return: route name as a string
    """
    # remove base url
    route = str(request.url)[len(str(request.base_url)) :]
    # remove query parameters
    if "?" in str(request.url):
        route = route[: route.find("?")]
    # convert / to _ for route name
    route = route.replace("/", "_")
    return route[:max_length]  # ensure the route name does not exceed max_length


def add_dkist_middleware(
    app: FastAPI, tracer: Tracer, meter: Meter, excluded_urls: str | None = None
) -> None:
    """Add DKIST middleware to FastAPI application."""

    # parse the excluded URLs for instrumentation
    excluded_urls = parse_excluded_urls(excluded_urls)

    # Innermost middleware to add securityheaders
    secure_headers = Secure()

    async def _add_security_headers(request: Request, call_next):
        response = await call_next(request)
        await secure_headers.set_headers_async(response)
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=_add_security_headers)

    # Metering middleware to happen inside the trace
    async def _meter_request(request: Request, call_next):
        """
        Middleware to increment meters around request processing.
        """
        if excluded_urls and excluded_urls.url_disabled(str(request.url)):
            # if the URL is excluded from metrics, just process the request without tracing
            response = await call_next(request)
            return response

        # total number of requests received
        request_counter = meter.create_up_down_counter(
            name=f"{meter.name}.rest.request.counter",
            unit="1",
            description="The number of requests received",
        )
        request_counter.add(1)

        # total number of requests received by method
        request_method_counter = meter.create_up_down_counter(
            name=f"{meter.name}.rest.{request.method}.counter",
            unit="1",
            description="The number of requests received by method",
        )
        request_method_counter.add(1)

        # total number of requests received by route
        max_route_length = MAX_METRIC_NAME_LENGTH - len(f"{meter.name}.rest..counter")
        route = _parse_request_for_route(request, max_length=max_route_length)
        request_route_counter = meter.create_up_down_counter(
            name=f"{meter.name}.rest.{route}.counter",
            unit="1",
            description="The number of requests received by route",
        )
        request_route_counter.add(1)

        response = await call_next(request)
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=_meter_request)

    # Tracing middleware on the nearly outermost layer
    async def _trace_request(request: Request, call_next):
        """
        Middleware to trace requests and responses in FastAPI applications.
        """
        if excluded_urls and excluded_urls.url_disabled(str(request.url)):
            # if the URL is excluded from tracing, just process the request without tracing
            response = await call_next(request)
            return response

        with tracer.start_as_current_span("Process Request") as span:
            # annotate the span with request details
            span.set_attribute("conversation_id", request.state.conversation_id)
            span.set_attribute("request_method", request.method)
            span.set_attribute("request_url", str(request.url))
            # process the request
            response = await call_next(request)
            span.set_status(StatusCode.OK)
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=_trace_request)

    # Add Tracking headers middleware to outermost layer
    async def _add_tracking_headers(request: Request, call_next):
        """
        Middleware to add tracking headers to the response.
        """
        # start time of request evaluation
        request.state.start_time = datetime.now()
        # id used for correlating log entries
        request.state.conversation_id = uuid4().hex
        response = await call_next(request)
        # include conversation id in response for log correlation
        response.headers["X-Conversation-Id"] = request.state.conversation_id
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=_add_tracking_headers)

    logger.info("DKIST middleware added to FastAPI application.")
