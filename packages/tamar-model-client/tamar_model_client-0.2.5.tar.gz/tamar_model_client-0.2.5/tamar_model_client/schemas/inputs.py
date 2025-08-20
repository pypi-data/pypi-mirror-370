import mimetypes
import os

import httpx
from google.genai import types
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body, FileTypes
from openai.types import ChatModel, Metadata, ReasoningEffort, ResponsesModel, Reasoning, ImageModel
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionAudioParam, completion_create_params, \
    ChatCompletionPredictionContentParam, ChatCompletionStreamOptionsParam, ChatCompletionToolChoiceOptionParam, \
    ChatCompletionToolParam
from openai.types.responses import ResponseInputParam, ResponseIncludable, ResponseTextConfigParam, \
    response_create_params, ToolParam
from openai.types.responses.response_prompt_param import ResponsePromptParam
from pydantic import BaseModel, model_validator, field_validator
from typing import List, Optional, Union, Iterable, Dict, Literal

from tamar_model_client.enums import ProviderType, InvokeType
from tamar_model_client.enums.channel import Channel
from tamar_model_client.utils import convert_file_field, validate_fields_by_provider_and_invoke_type


class UserContext(BaseModel):
    org_id: str  # 组织id
    user_id: str  # 用户id
    client_type: str  # 客户端类型，这里记录的是哪个服务请求过来的


class GoogleGenAiInput(BaseModel):
    model: str
    contents: Union[types.ContentListUnion, types.ContentListUnionDict]
    config: Optional[types.GenerateContentConfigOrDict] = None

    model_config = {
        "arbitrary_types_allowed": True
    }


class GoogleVertexAIImagesInput(BaseModel):
    model: str
    prompt: str
    negative_prompt: Optional[str] = None
    number_of_images: int = 1
    aspect_ratio: Optional[Literal["1:1", "9:16", "16:9", "4:3", "3:4"]] = None
    guidance_scale: Optional[float] = None
    language: Optional[str] = None
    seed: Optional[int] = None
    output_gcs_uri: Optional[str] = None
    add_watermark: Optional[bool] = True
    safety_filter_level: Optional[
        Literal["block_most", "block_some", "block_few", "block_fewest"]
    ] = None
    person_generation: Optional[
        Literal["dont_allow", "allow_adult", "allow_all"]
    ] = None

    model_config = {
        "arbitrary_types_allowed": True
    }


class GoogleGenAIImagesInput(BaseModel):
    model: str
    prompt: str
    config: Optional[types.GenerateImagesConfigOrDict] = None

    model_config = {
        "arbitrary_types_allowed": True
    }


class OpenAIResponsesInput(BaseModel):
    background: Optional[bool] | NotGiven = NOT_GIVEN
    include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN
    input: Union[str, ResponseInputParam] | NotGiven = NOT_GIVEN
    instructions: Optional[str] | NotGiven = NOT_GIVEN
    max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN
    max_tool_calls: Optional[int] | NotGiven = NOT_GIVEN
    metadata: Optional[Metadata] | NotGiven = NOT_GIVEN
    model: ResponsesModel | NotGiven = NOT_GIVEN
    parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN
    previous_response_id: Optional[str] | NotGiven = NOT_GIVEN
    prompt: Optional[ResponsePromptParam] | NotGiven = NOT_GIVEN
    prompt_cache_key: str | NotGiven = NOT_GIVEN
    reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN
    safety_identifier: str | NotGiven = NOT_GIVEN
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | NotGiven = NOT_GIVEN
    store: Optional[bool] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    stream_options: Optional[response_create_params.StreamOptions] | NotGiven = NOT_GIVEN
    temperature: Optional[float] | NotGiven = NOT_GIVEN
    text: ResponseTextConfigParam | NotGiven = NOT_GIVEN
    tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN
    tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN
    top_logprobs: Optional[int] | NotGiven = NOT_GIVEN
    top_p: Optional[float] | NotGiven = NOT_GIVEN
    truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    verbosity: Optional[Literal["low", "medium", "high"]] | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }


class OpenAIChatCompletionsInput(BaseModel):
    messages: Iterable[ChatCompletionMessageParam]
    model: Union[str, ChatModel]
    audio: Optional[ChatCompletionAudioParam] | NotGiven = NOT_GIVEN
    frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN
    function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN
    functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN
    logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN
    logprobs: Optional[bool] | NotGiven = NOT_GIVEN
    max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN
    max_tokens: Optional[int] | NotGiven = NOT_GIVEN
    metadata: Optional[Metadata] | NotGiven = NOT_GIVEN
    modalities: Optional[List[Literal["text", "audio"]]] | NotGiven = NOT_GIVEN
    n: Optional[int] | NotGiven = NOT_GIVEN
    parallel_tool_calls: bool | NotGiven = NOT_GIVEN
    prediction: Optional[ChatCompletionPredictionContentParam] | NotGiven = NOT_GIVEN
    presence_penalty: Optional[float] | NotGiven = NOT_GIVEN
    prompt_cache_key: str | NotGiven = NOT_GIVEN
    reasoning_effort: Optional[ReasoningEffort] | NotGiven = NOT_GIVEN
    response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN
    safety_identifier: str | NotGiven = NOT_GIVEN
    seed: Optional[int] | NotGiven = NOT_GIVEN
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | NotGiven = NOT_GIVEN
    stop: Union[Optional[str], List[str], None] | NotGiven = NOT_GIVEN
    store: Optional[bool] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    stream_options: Optional[ChatCompletionStreamOptionsParam] | NotGiven = NOT_GIVEN
    temperature: Optional[float] | NotGiven = NOT_GIVEN
    tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN
    tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN
    top_logprobs: Optional[int] | NotGiven = NOT_GIVEN
    top_p: Optional[float] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    verbosity: Optional[Literal["low", "medium", "high"]] | NotGiven = NOT_GIVEN
    web_search_options: completion_create_params.WebSearchOptions | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }


class OpenAIImagesInput(BaseModel):
    prompt: str
    background: Optional[Literal["transparent", "opaque", "auto"]] | NotGiven = NOT_GIVEN
    model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN
    moderation: Optional[Literal["low", "auto"]] | NotGiven = NOT_GIVEN
    n: Optional[int] | NotGiven = NOT_GIVEN
    output_compression: Optional[int] | NotGiven = NOT_GIVEN
    output_format: Optional[Literal["png", "jpeg", "webp"]] | NotGiven = NOT_GIVEN
    partial_images: Optional[int] | NotGiven = NOT_GIVEN
    quality: Optional[Literal["standard", "hd", "low", "medium", "high", "auto"]] | NotGiven = NOT_GIVEN
    response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN
    size: Optional[Literal[
        "auto", "1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"]] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    style: Optional[Literal["vivid", "natural"]] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }


class OpenAIImagesEditInput(BaseModel):
    image: Union[FileTypes, List[FileTypes]]
    prompt: str
    background: Optional[Literal["transparent", "opaque", "auto"]] | NotGiven = NOT_GIVEN
    input_fidelity: Optional[Literal["high", "low"]] | NotGiven = NOT_GIVEN
    mask: FileTypes | NotGiven = NOT_GIVEN
    model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN
    n: Optional[int] | NotGiven = NOT_GIVEN
    output_compression: Optional[int] | NotGiven = NOT_GIVEN
    output_format: Optional[Literal["png", "jpeg", "webp"]] | NotGiven = NOT_GIVEN
    partial_images: Optional[int] | NotGiven = NOT_GIVEN
    quality: Optional[Literal["standard", "low", "medium", "high", "auto"]] | NotGiven = NOT_GIVEN
    response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN
    size: Optional[Literal["256x256", "512x512", "1024x1024", "1536x1024", "1024x1536", "auto"]] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }


class BaseRequest(BaseModel):
    provider: ProviderType  # 供应商，如 "openai", "google" 等
    channel: Channel = Channel.NORMAL  # 渠道：不同服务商之前有不同的调用SDK，这里指定是调用哪个SDK
    invoke_type: InvokeType = InvokeType.GENERATION  # 模型调用类型：generation-生成模型调用


class ModelRequestInput(BaseRequest):
    # 合并 model 字段
    model: Optional[Union[str, ResponsesModel, ChatModel, ImageModel]] = None

    # OpenAI Responses Input（合并）
    input: Optional[Union[str, ResponseInputParam]] = None
    include: Optional[Union[List[ResponseIncludable], NotGiven]] = NOT_GIVEN
    instructions: Optional[Union[str, NotGiven]] = NOT_GIVEN
    max_output_tokens: Optional[Union[int, NotGiven]] = NOT_GIVEN
    max_tool_calls: Optional[Union[int, NotGiven]] = NOT_GIVEN
    metadata: Optional[Union[Metadata, NotGiven]] = NOT_GIVEN
    parallel_tool_calls: Optional[Union[bool, NotGiven]] = NOT_GIVEN
    previous_response_id: Optional[Union[str, NotGiven]] = NOT_GIVEN
    # prompt 同名字段合并：Responses 的 ResponsePromptParam + 图片生成的 str
    prompt: Optional[Union[str, ResponsePromptParam, NotGiven]] = NOT_GIVEN
    prompt_cache_key: Optional[Union[str, NotGiven]] = NOT_GIVEN
    reasoning: Optional[Union[Reasoning, NotGiven]] = NOT_GIVEN
    safety_identifier: Optional[Union[str, NotGiven]] = NOT_GIVEN
    service_tier: Optional[Union[Literal["auto", "default", "flex", "scale", "priority"], NotGiven]] = NOT_GIVEN
    store: Optional[Union[bool, NotGiven]] = NOT_GIVEN
    stream: Optional[Union[Literal[False], Literal[True], NotGiven]] = NOT_GIVEN
    # 合并两套 stream_options 类型
    stream_options: Optional[
        Union[response_create_params.StreamOptions, ChatCompletionStreamOptionsParam, NotGiven]] = NOT_GIVEN
    temperature: Optional[Union[float, NotGiven]] = NOT_GIVEN
    text: Optional[Union[ResponseTextConfigParam, NotGiven]] = NOT_GIVEN
    tool_choice: Optional[
        Union[response_create_params.ToolChoice, ChatCompletionToolChoiceOptionParam, NotGiven]
    ] = NOT_GIVEN
    tools: Optional[Union[Iterable[ToolParam], Iterable[ChatCompletionToolParam], NotGiven]] = NOT_GIVEN
    top_logprobs: Optional[Union[int, NotGiven]] = NOT_GIVEN
    top_p: Optional[Union[float, NotGiven]] = NOT_GIVEN
    truncation: Optional[Union[Literal["auto", "disabled"], NotGiven]] = NOT_GIVEN
    user: Optional[Union[str, NotGiven]] = NOT_GIVEN
    verbosity: Optional[Union[Literal["low", "medium", "high"], NotGiven]] = NOT_GIVEN

    extra_headers: Optional[Union[Headers, None]] = None
    extra_query: Optional[Union[Query, None]] = None
    extra_body: Optional[Union[Body, None]] = None
    timeout: Optional[Union[float, httpx.Timeout, None, NotGiven]] = NOT_GIVEN

    # OpenAI Chat Completions Input（合并）
    messages: Optional[Iterable[ChatCompletionMessageParam]] = None
    audio: Optional[Union[ChatCompletionAudioParam, NotGiven]] = NOT_GIVEN
    frequency_penalty: Optional[Union[float, NotGiven]] = NOT_GIVEN
    function_call: Optional[Union[completion_create_params.FunctionCall, NotGiven]] = NOT_GIVEN
    functions: Optional[Union[Iterable[completion_create_params.Function], NotGiven]] = NOT_GIVEN
    logit_bias: Optional[Union[Dict[str, int], NotGiven]] = NOT_GIVEN
    logprobs: Optional[Union[bool, NotGiven]] = NOT_GIVEN
    max_completion_tokens: Optional[Union[int, NotGiven]] = NOT_GIVEN
    max_tokens: Optional[Union[int, NotGiven]] = NOT_GIVEN
    modalities: Optional[Union[List[Literal["text", "audio"]], NotGiven]] = NOT_GIVEN
    n: Optional[Union[int, NotGiven]] = NOT_GIVEN  # 复用给 Chat 和 Images
    prediction: Optional[Union[ChatCompletionPredictionContentParam, NotGiven]] = NOT_GIVEN
    presence_penalty: Optional[Union[float, NotGiven]] = NOT_GIVEN
    reasoning_effort: Optional[Union[ReasoningEffort, NotGiven]] = NOT_GIVEN
    response_format: Optional[
        Union[completion_create_params.ResponseFormat, Literal["url", "b64_json"], NotGiven]
    ] = NOT_GIVEN
    seed: Optional[Union[int, NotGiven]] = NOT_GIVEN  # Chat/Vertex Images 共用
    web_search_options: Optional[Union[completion_create_params.WebSearchOptions, NotGiven]] = NOT_GIVEN

    # Google GenAI Input
    contents: Optional[Union[types.ContentListUnion, types.ContentListUnionDict]] = None
    config: Optional[Union[types.GenerateContentConfigOrDict, types.GenerateImagesConfigOrDict]] = None

    # Images（OpenAI Images / Images Edit / Google Vertex Images 合并）
    image: Optional[Union[FileTypes, List[FileTypes]]] = None
    # background 同名字段合并：Responses 的 bool（后台任务）+ Images 的透明度枚举
    background: Optional[Union[bool, Literal["transparent", "opaque", "auto"], NotGiven]] = NOT_GIVEN
    moderation: Optional[Union[Literal["low", "auto"], NotGiven]] = NOT_GIVEN
    input_fidelity: Optional[Union[Literal["high", "low"], NotGiven]] = NOT_GIVEN
    output_compression: Optional[Union[int, NotGiven]] = NOT_GIVEN
    output_format: Optional[Union[Literal["png", "jpeg", "webp"], NotGiven]] = NOT_GIVEN
    partial_images: Optional[Union[int, NotGiven]] = NOT_GIVEN
    mask: Union[FileTypes, NotGiven] = NOT_GIVEN
    negative_prompt: Optional[str] = None
    aspect_ratio: Optional[Literal["1:1", "9:16", "16:9", "4:3", "3:4"]] = None
    guidance_scale: Optional[float] = None
    language: Optional[str] = None
    output_gcs_uri: Optional[str] = None
    add_watermark: Optional[bool] = None
    safety_filter_level: Optional[Literal["block_most", "block_some", "block_few", "block_fewest"]] = None
    person_generation: Optional[Literal["dont_allow", "allow_adult", "allow_all"]] = None
    quality: Optional[Union[Literal["standard", "hd", "low", "medium", "high", "auto"], NotGiven]] = NOT_GIVEN
    size: Optional[
        Union[
            Literal["auto", "1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"],
            NotGiven,
        ]
    ] = NOT_GIVEN
    style: Optional[Union[Literal["vivid", "natural"], NotGiven]] = NOT_GIVEN
    number_of_images: Optional[int] = None  # Google 用法

    model_config = {
        "arbitrary_types_allowed": True
    }

    @field_validator("image", mode="before")
    @classmethod
    def validate_image(cls, v):
        return convert_file_field(v)

    @field_validator("mask", mode="before")
    @classmethod
    def validate_mask(cls, v):
        return convert_file_field(v)


class ModelRequest(ModelRequestInput):
    user_context: UserContext  # 用户信息

    @model_validator(mode="after")
    def validate_by_provider_and_invoke_type(self) -> "ModelRequest":
        return validate_fields_by_provider_and_invoke_type(
            instance=self,
            extra_allowed_fields={"provider", "channel", "invoke_type", "user_context"},
        )


class BatchModelRequestItem(ModelRequestInput):
    custom_id: Optional[str] = None
    priority: Optional[int] = None  # （可选、预留字段）批量调用时执行的优先级

    @model_validator(mode="after")
    def validate_by_provider_and_invoke_type(self) -> "BatchModelRequestItem":
        return validate_fields_by_provider_and_invoke_type(
            instance=self,
            extra_allowed_fields={"provider", "channel", "invoke_type", "user_context", "custom_id"},
        )


class BatchModelRequest(BaseModel):
    user_context: UserContext  # 用户信息
    items: List[BatchModelRequestItem]  # 批量请求项列表
