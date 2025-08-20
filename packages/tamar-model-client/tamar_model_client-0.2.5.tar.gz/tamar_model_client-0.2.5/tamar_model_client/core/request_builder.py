"""
Request building logic for Tamar Model Client

This module handles the construction of gRPC request objects from
model request objects, including provider-specific field validation.
"""

import json
from typing import Dict, Any, Set

from ..enums import ProviderType, InvokeType
from ..generated import model_service_pb2
from ..schemas.inputs import (
    ModelRequest,
    BatchModelRequest,
    BatchModelRequestItem,
    UserContext,
    GoogleGenAiInput,
    GoogleVertexAIImagesInput,
    GoogleGenAIImagesInput,
    OpenAIResponsesInput,
    OpenAIChatCompletionsInput,
    OpenAIImagesInput,
    OpenAIImagesEditInput
)
from .utils import is_effective_value, serialize_value, remove_none_from_dict


class RequestBuilder:
    """
    请求构建器
    
    负责将高级的 ModelRequest 对象转换为 gRPC 协议所需的请求对象，
    包括参数验证、序列化和提供商特定的字段处理。
    """

    @staticmethod
    def get_allowed_fields(provider: ProviderType, invoke_type: InvokeType) -> Set[str]:
        """
        获取特定提供商和调用类型组合所允许的字段
        
        Args:
            provider: 提供商类型
            invoke_type: 调用类型
            
        Returns:
            Set[str]: 允许的字段名集合
            
        Raises:
            ValueError: 当提供商和调用类型组合不受支持时
        """
        match (provider, invoke_type):
            case (ProviderType.GOOGLE, InvokeType.GENERATION):
                return set(GoogleGenAiInput.model_fields.keys())
            case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION):
                return set(GoogleVertexAIImagesInput.model_fields.keys())
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.RESPONSES | InvokeType.GENERATION):
                return set(OpenAIResponsesInput.model_fields.keys())
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.CHAT_COMPLETIONS):
                return set(OpenAIChatCompletionsInput.model_fields.keys())
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_GENERATION):
                return set(OpenAIImagesInput.model_fields.keys())
            case ((ProviderType.OPENAI | ProviderType.AZURE), InvokeType.IMAGE_EDIT_GENERATION):
                return set(OpenAIImagesEditInput.model_fields.keys())
            case (ProviderType.GOOGLE, InvokeType.IMAGE_GENERATION_GENAI):
                return set(GoogleGenAIImagesInput.model_fields.keys())
            case _:
                raise ValueError(
                    f"Unsupported provider/invoke_type combination: {provider} + {invoke_type}"
                )

    @staticmethod
    def build_grpc_extra_fields(model_request: ModelRequest) -> Dict[str, Any]:
        """
        构建 gRPC 请求的额外字段
        
        根据提供商和调用类型，过滤并序列化请求中的参数。
        
        Args:
            model_request: 模型请求对象
            
        Returns:
            Dict[str, Any]: 序列化后的额外字段字典
            
        Raises:
            ValueError: 当构建请求失败时
        """
        try:
            # 获取允许的字段集合
            allowed_fields = RequestBuilder.get_allowed_fields(
                model_request.provider,
                model_request.invoke_type
            )

            # 将 ModelRequest 转换为字典，只包含已设置的字段
            model_request_dict = model_request.model_dump(exclude_unset=True)

            # 构建 gRPC 请求参数
            grpc_request_kwargs = {}
            for field in allowed_fields:
                if field in model_request_dict:
                    value = model_request_dict[field]

                    # 跳过无效的值
                    if not is_effective_value(value):
                        continue

                    # 序列化不支持的类型
                    grpc_request_kwargs[field] = serialize_value(value)

            # 清理序列化后的参数中的 None 值
            grpc_request_kwargs = remove_none_from_dict(grpc_request_kwargs)

            return grpc_request_kwargs

        except Exception as e:
            raise ValueError(f"构建请求失败: {str(e)}") from e

    @staticmethod
    def build_single_request(model_request: ModelRequest) -> model_service_pb2.ModelRequestItem:
        """
        构建单个模型请求的 gRPC 对象
        
        Args:
            model_request: 模型请求对象
            
        Returns:
            model_service_pb2.ModelRequestItem: gRPC 请求对象
            
        Raises:
            ValueError: 当构建请求失败时
        """
        # 构建额外字段
        extra_fields = RequestBuilder.build_grpc_extra_fields(model_request)

        # 创建 gRPC 请求对象
        return model_service_pb2.ModelRequestItem(
            provider=model_request.provider.value,
            channel=model_request.channel.value if model_request.channel else "",
            invoke_type=model_request.invoke_type.value,
            stream=model_request.stream or False,
            org_id=model_request.user_context.org_id or "",
            user_id=model_request.user_context.user_id or "",
            client_type=model_request.user_context.client_type or "",
            extra=extra_fields
        )

    @staticmethod
    def build_batch_request_item(
            batch_item: "BatchModelRequestItem",
            user_context: "UserContext"
    ) -> model_service_pb2.ModelRequestItem:
        """
        构建批量请求中的单个项目
        
        Args:
            batch_item: 批量请求项
            user_context: 用户上下文（来自父BatchModelRequest）
            
        Returns:
            model_service_pb2.ModelRequestItem: gRPC 请求对象
        """
        # 构建额外字段
        extra_fields = RequestBuilder.build_grpc_extra_fields(batch_item)

        # 添加 custom_id 如果存在
        if hasattr(batch_item, 'custom_id') and batch_item.custom_id:
            request_item = model_service_pb2.ModelRequestItem(
                provider=batch_item.provider.value,
                channel=batch_item.channel.value if batch_item.channel else "",
                invoke_type=batch_item.invoke_type.value,
                stream=batch_item.stream or False,
                org_id=user_context.org_id or "",
                user_id=user_context.user_id or "",
                client_type=user_context.client_type or "",
                custom_id=batch_item.custom_id,
                extra=extra_fields
            )
        else:
            request_item = model_service_pb2.ModelRequestItem(
                provider=batch_item.provider.value,
                channel=batch_item.channel.value if batch_item.channel else "",
                invoke_type=batch_item.invoke_type.value,
                stream=batch_item.stream or False,
                org_id=user_context.org_id or "",
                user_id=user_context.user_id or "",
                client_type=user_context.client_type or "",
                extra=extra_fields
            )

        # 添加 priority 如果存在
        if hasattr(batch_item, 'priority') and batch_item.priority is not None:
            request_item.priority = batch_item.priority

        return request_item

    @staticmethod
    def build_batch_request(batch_request: BatchModelRequest) -> model_service_pb2.ModelRequest:
        """
        构建批量请求的 gRPC 对象
        
        Args:
            batch_request: 批量请求对象
            
        Returns:
            model_service_pb2.ModelRequest: gRPC 批量请求对象
            
        Raises:
            ValueError: 当构建请求失败时
        """
        items = []

        for batch_item in batch_request.items:
            # 为每个请求项构建 gRPC 对象，传入 user_context
            request_item = RequestBuilder.build_batch_request_item(
                batch_item,
                batch_request.user_context
            )
            items.append(request_item)

        # 创建批量请求对象
        return model_service_pb2.ModelRequest(
            items=items
        )
