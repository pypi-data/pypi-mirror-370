from openai import NotGiven
from pydantic import BaseModel
from typing import Any
import os, mimetypes


def convert_file_field(value: Any) -> Any:
    def is_file_like(obj):
        return hasattr(obj, "read") and callable(obj.read)

    def infer_mimetype(filename: str) -> str:
        mime, _ = mimetypes.guess_type(filename)
        return mime or "application/octet-stream"

    def convert_item(item):
        if is_file_like(item):
            filename = os.path.basename(getattr(item, "name", "file.png"))
            content_type = infer_mimetype(filename)
            content = item.read()
            if hasattr(item, "seek"):
                item.seek(0)
            return (filename, content, content_type)
        elif isinstance(item, tuple):
            parts = list(item)
            if len(parts) > 1:
                maybe_file = parts[1]
                if is_file_like(maybe_file):
                    content = maybe_file.read()
                    if hasattr(maybe_file, "seek"):
                        maybe_file.seek(0)
                    parts[1] = content
                elif not isinstance(maybe_file, (bytes, bytearray)):
                    raise ValueError(f"Unsupported second element in tuple: {type(maybe_file)}")
            if len(parts) == 2:
                parts.append(infer_mimetype(os.path.basename(parts[0] or "file.png")))
            return tuple(parts)
        else:
            return item

    if value is None:
        return value
    elif isinstance(value, list):
        return [convert_item(v) for v in value]
    else:
        return convert_item(value)


def validate_fields_by_provider_and_invoke_type(
        instance: BaseModel,
        extra_allowed_fields: set[str],
        extra_required_fields: set[str] = set()
) -> BaseModel:
    """
    通用的字段校验逻辑，根据 provider 和 invoke_type 动态检查字段合法性和必填字段。
    适用于 ModelRequest 和 BatchModelRequestItem。
    """
    from tamar_model_client.enums import ProviderType, InvokeType
    from tamar_model_client.schemas.inputs import GoogleGenAiInput, OpenAIResponsesInput, OpenAIChatCompletionsInput, \
        OpenAIImagesInput, OpenAIImagesEditInput, GoogleVertexAIImagesInput, GoogleGenAIImagesInput

    google_allowed = extra_allowed_fields | set(GoogleGenAiInput.model_fields)
    openai_responses_allowed = extra_allowed_fields | set(OpenAIResponsesInput.model_fields)
    openai_chat_allowed = extra_allowed_fields | set(OpenAIChatCompletionsInput.model_fields)
    openai_images_allowed = extra_allowed_fields | set(OpenAIImagesInput.model_fields)
    openai_images_edit_allowed = extra_allowed_fields | set(OpenAIImagesEditInput.model_fields)
    google_vertexai_images_allowed = extra_allowed_fields | set(GoogleVertexAIImagesInput.model_fields)
    google_genai_images_allowed = extra_allowed_fields | set(GoogleGenAIImagesInput.model_fields)

    google_required = {"model", "contents"}
    google_vertex_required = {"model", "prompt"}
    google_genai_images_required = {"model", "prompt"}
    openai_resp_required = {"input", "model"}
    openai_chat_required = {"messages", "model"}
    openai_img_required = {"prompt"}
    openai_edit_required = {"image", "prompt"}

    match (instance.provider, instance.invoke_type):
        case (ProviderType.GOOGLE, InvokeType.GENERATION):
            allowed = google_allowed
            required = google_required
        case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION):
            allowed = google_vertexai_images_allowed
            required = google_vertex_required
        case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.RESPONSES | InvokeType.GENERATION):
            allowed = openai_responses_allowed
            required = openai_resp_required
        case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.CHAT_COMPLETIONS):
            allowed = openai_chat_allowed
            required = openai_chat_required
        case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_GENERATION):
            allowed = openai_images_allowed
            required = openai_img_required
        case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_EDIT_GENERATION):
            allowed = openai_images_edit_allowed
            required = openai_edit_required
        case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION_GENAI):
            allowed = google_genai_images_allowed
            required = google_genai_images_required
        case _:
            raise ValueError(f"Unsupported provider/invoke_type: {instance.provider} + {instance.invoke_type}")

    required = required | extra_required_fields

    missing = [f for f in required if getattr(instance, f, None) is None]
    if missing:
        raise ValueError(
            f"Missing required fields for provider={instance.provider} and invoke_type={instance.invoke_type}: {missing}")

    illegal = []
    valid_fields = {"provider", "channel", "invoke_type"}
    if getattr(instance, "stream", None) is not None:
        valid_fields.add("stream")

    for k, v in instance.__dict__.items():
        if k in valid_fields:
            continue
        if k not in allowed and v is not None and not isinstance(v, NotGiven):
            illegal.append(k)

    if illegal:
        raise ValueError(
            f"Unsupported fields for provider={instance.provider} and invoke_type={instance.invoke_type}: {illegal}")

    return instance
