import atexit

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from agentlens.config import get_config
from agentlens.exporter import SplunkHECSpanExporter
from agentlens.version import __version__

_provider: TracerProvider | None = None


def instrument(service_name: str = None) -> None:
    global _provider

    config = get_config()
    resolved_name = service_name or config.service_name

    resource = Resource.create(
        {
            "service.name": resolved_name,
            "service.version": __version__,
        }
    )

    exporter = SplunkHECSpanExporter()
    processor = BatchSpanProcessor(exporter)

    _provider = TracerProvider(resource=resource)
    _provider.add_span_processor(processor)

    try:
        from openinference.instrumentation.crewai import CrewAIInstrumentor
        CrewAIInstrumentor().instrument(tracer_provider=_provider)
    except Exception:
        pass

    try:
        from openinference.instrumentation.langchain import LangChainInstrumentor
        LangChainInstrumentor().instrument(tracer_provider=_provider)
    except Exception:
        pass

    try:
        from openinference.instrumentation.openai import OpenAIInstrumentor
        OpenAIInstrumentor().instrument(tracer_provider=_provider)
    except Exception:
        pass

    atexit.register(shutdown)


def shutdown() -> None:
    global _provider
    if _provider is not None:
        _provider.shutdown()
        _provider = None
