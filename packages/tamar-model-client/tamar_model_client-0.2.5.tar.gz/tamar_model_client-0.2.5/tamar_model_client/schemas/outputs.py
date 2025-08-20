from typing import Any, Iterator, Optional, Union, Dict, List

from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    content: Optional[str] = None  # 文本输出内容
    usage: Optional[Dict] = None  # tokens / 请求成本等（JSON）
    stream_response: Optional[Union[Iterator[str], Any]] = None  # 用于流式响应（同步 or 异步）
    raw_response: Optional[Union[Dict, List]] = None  # 模型服务商返回的原始结构（JSON）
    error: Optional[Any] = None  # 错误信息
    custom_id: Optional[str] = None  # 自定义ID，用于批量请求时结果关联


class ModelResponse(BaseResponse):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    request_id: Optional[str] = None  # 请求ID，用于跟踪请求


class BatchModelResponse(BaseModel):
    request_id: Optional[str] = None  # 请求ID，用于跟踪请求
    responses: Optional[List[BaseResponse]] = None  # 批量请求的响应列表
