from typing import Any

from llama_index.core.callbacks.base_handler import BaseCallbackHandler

from openinference.instrumentation import TraceConfig
def arize_phoenix_callback_handler(**kwargs: Any) -> BaseCallbackHandler:
    # newer versions of arize, v2.x
    try:
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk import trace as trace_sdk
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor

        endpoint = kwargs.get("endpoint", "http://127.0.0.1:6006/v1/traces")
        tracer_provider = trace_sdk.TracerProvider()
        tracer_provider.add_span_processor(
            SimpleSpanProcessor(OTLPSpanExporter(endpoint))
        )
        config = TraceConfig(
            base64_image_max_length=640000
        )

        return LlamaIndexInstrumentor().instrument(
            tracer_provider=kwargs.get("tracer_provider", tracer_provider),
            separate_trace_from_runtime_context=kwargs.get(
                "separate_trace_from_runtime_context"
            ),
            config=config
        )
    except ImportError:
        raise ImportError("Arize Phoenix is not installed. Please install it using `pip install arize-phoenix`")
