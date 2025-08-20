"""
Response handling logic for Tamar Model Client

This module provides utilities for processing gRPC responses and
converting them to client response objects.
"""

import json
from typing import Optional, Dict, Any

from ..schemas import ModelResponse, BatchModelResponse


class ResponseHandler:
    """
    响应处理器
    
    负责将 gRPC 响应转换为客户端响应对象，
    包括 JSON 解析、错误处理和数据结构转换。
    """
    
    @staticmethod
    def build_model_response(grpc_response) -> ModelResponse:
        """
        从 gRPC 响应构建 ModelResponse 对象
        
        Args:
            grpc_response: gRPC 服务返回的响应对象
            
        Returns:
            ModelResponse: 客户端响应对象
        """
        return ModelResponse(
            content=grpc_response.content,
            usage=ResponseHandler._parse_json_field(grpc_response.usage),
            error=grpc_response.error or None,
            raw_response=ResponseHandler._parse_json_field(grpc_response.raw_response),
            request_id=grpc_response.request_id if grpc_response.request_id else None,
        )
    
    @staticmethod
    def build_batch_response(grpc_response) -> BatchModelResponse:
        """
        从 gRPC 批量响应构建 BatchModelResponse 对象
        
        Args:
            grpc_response: gRPC 服务返回的批量响应对象
            
        Returns:
            BatchModelResponse: 客户端批量响应对象
        """
        responses = []
        for response_item in grpc_response.items:
            model_response = ResponseHandler.build_model_response(response_item)
            responses.append(model_response)
        
        return BatchModelResponse(
            responses=responses,
            request_id=grpc_response.request_id if grpc_response.request_id else None
        )
    
    @staticmethod
    def _parse_json_field(json_str: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        安全地解析 JSON 字符串
        
        Args:
            json_str: 待解析的 JSON 字符串
            
        Returns:
            Optional[Dict[str, Any]]: 解析后的字典，或 None（如果输入为空）
        """
        if not json_str:
            return None
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始字符串作为错误信息
            return {"error": "JSON parse error", "raw": json_str}
    
    @staticmethod
    def build_log_data(
        model_request,
        response: Optional[ModelResponse] = None,
        duration: Optional[float] = None,
        error: Optional[Exception] = None,
        stream_stats: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        构建日志数据
        
        为请求和响应日志构建结构化的数据字典。
        
        Args:
            model_request: 原始请求对象
            response: 响应对象（可选）
            duration: 请求持续时间（秒）
            error: 错误对象（可选）
            stream_stats: 流式响应统计信息（可选）
            
        Returns:
            Dict[str, Any]: 日志数据字典
        """
        data = {
            "provider": model_request.provider.value,
            "invoke_type": model_request.invoke_type.value,
            "model": getattr(model_request, 'model', None),
            "stream": getattr(model_request, 'stream', False),
        }
        
        # 添加用户上下文信息（如果有）
        if hasattr(model_request, 'user_context'):
            data.update({
                "org_id": model_request.user_context.org_id,
                "user_id": model_request.user_context.user_id,
                "client_type": model_request.user_context.client_type
            })
        
        # 添加响应信息
        if response:
            if hasattr(response, 'content') and response.content:
                data["content_length"] = len(response.content)
            if hasattr(response, 'usage'):
                data["usage"] = response.usage
        
        # 添加流式响应统计
        if stream_stats:
            data.update(stream_stats)
        
        # 添加错误信息
        if error:
            data["error_type"] = type(error).__name__
            data["error_message"] = str(error)
        
        return data