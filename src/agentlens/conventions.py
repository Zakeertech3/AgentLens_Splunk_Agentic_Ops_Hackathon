ATTRIBUTE_MAP = {
    "openinference.span.kind": "span_kind",
    "llm.model_name": "model",
    "llm.token_count.prompt": "tokens_prompt",
    "llm.token_count.completion": "tokens_completion",
    "llm.token_count.total": "tokens_total",
    "input.value": "prompt",
    "output.value": "response",
    "tool.name": "tool_name",
    "tool.parameters": "tool_params",
}

_TRUNCATE_FIELDS = {"prompt", "response"}
_TRUNCATE_LIMIT = 2000


def flatten_attributes(attrs: dict) -> dict:
    result = {}
    for key, value in attrs.items():
        clean_key = ATTRIBUTE_MAP.get(key, key)
        if clean_key in _TRUNCATE_FIELDS and isinstance(value, str):
            value = value[:_TRUNCATE_LIMIT]
        result[clean_key] = value
    return result
