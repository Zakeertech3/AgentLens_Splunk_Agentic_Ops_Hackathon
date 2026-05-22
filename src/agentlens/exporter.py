import json
import socket
from typing import Sequence

import httpx
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from rich.console import Console

from agentlens.config import get_config
from agentlens.conventions import flatten_attributes

_console = Console(stderr=True)
_hostname = socket.gethostname()


def _span_to_hec_event(span: ReadableSpan) -> dict:
    config = get_config()

    trace_id = format(span.context.trace_id, "032x") if span.context else ""
    span_id = format(span.context.span_id, "016x") if span.context else ""
    parent_span_id = format(span.parent.span_id, "016x") if span.parent else None

    start_ns = span.start_time or 0
    end_ns = span.end_time or 0
    duration_ms = (end_ns - start_ns) / 1_000_000

    attributes = flatten_attributes(dict(span.attributes)) if span.attributes else {}

    events = [
        {
            "name": e.name,
            "timestamp": e.timestamp / 1_000_000_000,
            "attributes": dict(e.attributes) if e.attributes else {},
        }
        for e in (span.events or [])
    ]

    service_name = (
        span.resource.attributes.get("service.name", config.service_name)
        if span.resource
        else config.service_name
    )

    return {
        "time": start_ns / 1_000_000_000,
        "host": _hostname,
        "source": "agentlens",
        "sourcetype": config.splunk_sourcetype,
        "index": config.splunk_index,
        "event": {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "name": span.name,
            "kind": span.kind.name if span.kind else "INTERNAL",
            "start_time": start_ns / 1_000_000_000,
            "end_time": end_ns / 1_000_000_000,
            "duration_ms": duration_ms,
            "status": span.status.status_code.name if span.status else "UNSET",
            "attributes": attributes,
            "events": events,
            "service_name": service_name,
        },
    }


class SplunkHECSpanExporter(SpanExporter):
    def __init__(self) -> None:
        self._config = get_config()
        self._client = httpx.Client(
            headers={
                "Authorization": f"Splunk {self._config.splunk_hec_token}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        if not self._config.enabled or not spans:
            return SpanExportResult.SUCCESS

        try:
            payload = "\n".join(json.dumps(_span_to_hec_event(s)) for s in spans)

            if self._config.debug:
                _console.print(f"HEC export: {len(spans)} span(s)", style="dim")

            response = self._client.post(
                self._config.splunk_hec_url,
                content=payload,
            )

            if response.status_code != 200:
                _console.print(
                    f"HEC export failed: HTTP {response.status_code} - {response.text}",
                    markup=False,
                )
                return SpanExportResult.FAILURE

            return SpanExportResult.SUCCESS

        except Exception as exc:
            _console.print(f"HEC export error: {exc}", markup=False)
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        self._client.close()
