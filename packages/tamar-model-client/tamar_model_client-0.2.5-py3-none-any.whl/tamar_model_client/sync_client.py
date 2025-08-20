"""
Tamar Model Client 同步客户端实现

本模块实现了同步的 gRPC 客户端，用于与 Model Manager Server 进行通信。
提供了与异步客户端相同的功能，但使用同步 API，适合在同步环境中使用。

主要功能：
- 同步 gRPC 通信
- JWT 认证
- 自动重试和错误处理
- 连接池管理
- 详细的日志记录

使用示例：
    with TamarModelClient() as client:
        request = ModelRequest(...)
        response = client.invoke(request)
        
注意：对于需要高并发的场景，建议使用 AsyncTamarModelClient
"""

import json
import logging
import random
import threading
import time
from typing import Optional, Union, Iterator

import grpc

from .core import (
    generate_request_id,
    set_request_id,
    set_origin_request_id,
    get_protected_logger,
    MAX_MESSAGE_LENGTH, 
    get_request_id,
    RequestIdManager
)
from .core.base_client import BaseClient
from .core.request_builder import RequestBuilder
from .core.response_handler import ResponseHandler
from .exceptions import ConnectionError, TamarModelException
from .generated import model_service_pb2, model_service_pb2_grpc
from .schemas import BatchModelResponse, ModelResponse
from .schemas.inputs import BatchModelRequest, ModelRequest
from .core.http_fallback import HttpFallbackMixin

# 配置日志记录器（使用受保护的logger）
logger = get_protected_logger(__name__)


class TamarModelClient(BaseClient, HttpFallbackMixin):
    """
    Tamar Model Client 同步客户端
    
    提供与 Model Manager Server 的同步通信能力，支持：
    - 单个和批量模型调用
    - 流式和非流式响应  
    - 自动重试和错误恢复
    - JWT 认证
    - 连接池管理
    
    使用示例：
        # 基本用法
        client = TamarModelClient()
        client.connect()
        
        request = ModelRequest(...)
        response = client.invoke(request)
        
        # 上下文管理器用法（推荐）
        with TamarModelClient() as client:
            response = client.invoke(request)
    
    环境变量配置：
        MODEL_MANAGER_SERVER_ADDRESS: gRPC 服务器地址
        MODEL_MANAGER_SERVER_JWT_SECRET_KEY: JWT 密钥
        MODEL_MANAGER_SERVER_GRPC_USE_TLS: 是否使用 TLS
        MODEL_MANAGER_SERVER_GRPC_MAX_RETRIES: 最大重试次数
        MODEL_MANAGER_SERVER_GRPC_RETRY_DELAY: 重试延迟
    """
    
    def __init__(self, **kwargs):
        """
        初始化同步客户端
        
        参数继承自 BaseClient，包括：
        - server_address: gRPC 服务器地址
        - jwt_secret_key: JWT 签名密钥
        - jwt_token: 预生成的 JWT 令牌
        - default_payload: JWT 令牌的默认载荷
        - token_expires_in: JWT 令牌过期时间
        - max_retries: 最大重试次数
        - retry_delay: 初始重试延迟
        """
        super().__init__(logger_name=__name__, **kwargs)
        
        # === gRPC 通道和连接管理 ===
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[model_service_pb2_grpc.ModelServiceStub] = None
        self._channel_error_count = 0
        self._last_channel_error_time = None
        self._channel_lock = threading.Lock()  # 线程安全的channel操作
        
        # === Request ID 管理 ===
        self._request_id_manager = RequestIdManager()

    def close(self):
        """
        关闭客户端连接
        
        优雅地关闭 gRPC 通道并清理资源。
        建议在程序结束前调用此方法，或使用上下文管理器自动管理。
        """
        if self.channel and not self._closed:
            self.channel.close()
            self._closed = True
            logger.info("🔒 gRPC channel closed",
                        extra={"log_type": "info", "data": {"status": "closed"}})

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def connect(self):
        """
        显式连接到服务器
        
        建立与 gRPC 服务器的连接。通常不需要手动调用，
        因为 invoke 方法会自动确保连接已建立。
        """
        self._ensure_initialized()

    def _ensure_initialized(self):
        """
        初始化gRPC通道
        
        确保gRPC通道和存根已正确初始化。如果初始化失败，
        会进行重试，支持TLS配置和完整的keepalive选项。
        
        连接配置包括：
        - 消息大小限制
        - Keepalive设置（30秒ping间隔，10秒超时）
        - 连接生命周期管理（1小时最大连接时间）
        - 性能优化选项（带宽探测、内置重试）
        
        Raises:
            ConnectionError: 当达到最大重试次数仍无法连接时
        """
        if self.channel and self.stub and self._is_channel_healthy():
            return
            
        # 如果 channel 存在但不健康，记录日志
        if self.channel and self.stub:
            logger.warning(
                "⚠️ Channel exists but unhealthy, will recreate",
                extra={
                    "log_type": "channel_recreate",
                    "data": {
                        "channel_error_count": self._channel_error_count,
                        "time_since_last_error": time.time() - self._last_channel_error_time if self._last_channel_error_time else None
                    }
                }
            )
            self._recreate_channel()

        retry_count = 0
        options = self.build_channel_options()

        while retry_count <= self.max_retries:
            try:
                if self.use_tls:
                    credentials = grpc.ssl_channel_credentials()
                    self.channel = grpc.secure_channel(
                        self.server_address,
                        credentials,
                        options=options
                    )
                    logger.info("🔐 Using secure gRPC channel (TLS enabled)",
                                extra={"log_type": "info",
                                       "data": {"tls_enabled": True, "server_address": self.server_address}})
                else:
                    self.channel = grpc.insecure_channel(
                        f"dns:///{self.server_address}",
                        options=options
                    )
                    logger.info("🔓 Using insecure gRPC channel (TLS disabled)",
                                extra={"log_type": "info",
                                       "data": {"tls_enabled": False, "server_address": self.server_address}})
                
                # 等待通道就绪
                grpc.channel_ready_future(self.channel).result(timeout=10)
                self.stub = model_service_pb2_grpc.ModelServiceStub(self.channel)
                logger.info(f"✅ gRPC channel initialized to {self.server_address}",
                            extra={"log_type": "info",
                                   "data": {"status": "success", "server_address": self.server_address}})
                return
                
            except grpc.FutureTimeoutError as e:
                logger.error(f"❌ gRPC channel initialization timed out: {str(e)}", exc_info=True,
                             extra={"log_type": "info",
                                    "data": {"error_type": "timeout", "server_address": self.server_address}})
            except grpc.RpcError as e:
                logger.error(f"❌ gRPC channel initialization failed: {str(e)}", exc_info=True,
                             extra={"log_type": "info",
                                    "data": {"error_type": "grpc_error", "server_address": self.server_address}})
            except Exception as e:
                logger.error(f"❌ Unexpected error during gRPC channel initialization: {str(e)}", exc_info=True,
                             extra={"log_type": "info",
                                    "data": {"error_type": "unknown", "server_address": self.server_address}})
            
            retry_count += 1
            if retry_count <= self.max_retries:
                time.sleep(self.retry_delay * retry_count)

        raise ConnectionError(f"Failed to connect to {self.server_address} after {self.max_retries} retries")
    
    def _is_channel_healthy(self) -> bool:
        """
        检查 channel 是否健康
        
        Returns:
            bool: True 如果 channel 健康，False 如果需要重建
        """
        if not self.channel:
            return False
            
        try:
            # 检查 channel 状态
            state = self.channel._channel.check_connectivity_state(False)
            
            # 如果处于关闭或失败状态，需要重建
            if state in [grpc.ChannelConnectivity.SHUTDOWN, 
                        grpc.ChannelConnectivity.TRANSIENT_FAILURE]:
                logger.warning(f"⚠️ Channel in unhealthy state: {state}",
                             extra={"log_type": "info", 
                                   "data": {"channel_state": str(state)}})
                return False
                
            # 如果最近有多次错误，也需要重建
            if self._channel_error_count > 3 and self._last_channel_error_time:
                if time.time() - self._last_channel_error_time < 60:  # 60秒内
                    logger.warning("⚠️ Too many channel errors recently, marking as unhealthy",
                                 extra={"log_type": "info",
                                       "data": {"error_count": self._channel_error_count}})
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking channel health: {e}",
                        extra={"log_type": "info", 
                              "data": {"error": str(e)}})
            return False
    
    def _recreate_channel(self):
        """
        重建 gRPC channel
        
        关闭旧的 channel 并创建新的连接
        """
        with self._channel_lock:
            # 关闭旧 channel
            if self.channel:
                try:
                    self.channel.close()
                    logger.info("🔚 Closed unhealthy channel",
                              extra={"log_type": "info"})
                except Exception as e:
                    logger.warning(f"⚠️ Error closing channel: {e}",
                                 extra={"log_type": "info"})
                    
            # 清空引用
            self.channel = None
            self.stub = None
            
            # 重置错误计数
            self._channel_error_count = 0
            self._last_channel_error_time = None
            
            logger.info("🔄 Recreating gRPC channel...",
                       extra={"log_type": "info"})
    
    def _record_channel_error(self, error: grpc.RpcError):
        """
        记录 channel 错误，用于健康检查
        
        Args:
            error: gRPC 错误
        """
        self._channel_error_count += 1
        self._last_channel_error_time = time.time()
        
        # 获取当前 channel 状态
        channel_state = None
        if self.channel:
            try:
                channel_state = self.channel._channel.check_connectivity_state(False)
            except:
                channel_state = "UNKNOWN"
        
        # 对于严重错误，增加错误权重
        if error.code() in [grpc.StatusCode.INTERNAL, 
                           grpc.StatusCode.UNAVAILABLE]:
            self._channel_error_count += 2
            
        # 记录详细的错误信息
        logger.warning(
            f"⚠️ Channel error recorded: {error.code().name}",
            extra={
                "log_type": "channel_error",
                "data": {
                    "error_code": error.code().name,
                    "error_count": self._channel_error_count,
                    "channel_state": str(channel_state) if channel_state else "NO_CHANNEL",
                    "time_since_last_error": time.time() - self._last_channel_error_time if self._last_channel_error_time else 0,
                    "error_details": error.details() if hasattr(error, 'details') else "",
                    "debug_string": error.debug_error_string() if hasattr(error, 'debug_error_string') else ""
                }
            }
        )

    def _retry_request(self, func, *args, **kwargs):
        """
        使用增强的错误处理器进行重试（同步版本）
        """
        # 记录方法开始时间
        method_start_time = time.time()
        
        # 从kwargs中提取request_id（如果有的话），然后移除它
        request_id = kwargs.pop('request_id', None) or get_request_id()
        
        # 构建请求上下文
        context = {
            'method': func.__name__ if hasattr(func, '__name__') else 'unknown',
            'client_version': 'sync',
            'request_id': request_id,
        }

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                context['retry_count'] = attempt
                return func(*args, **kwargs)

            except grpc.RpcError as e:
                # 使用新的错误处理逻辑
                context['retry_count'] = attempt
                current_duration = time.time() - method_start_time

                # 判断是否可以重试
                should_retry = self._should_retry(e, attempt)
                
                # 记录 channel 错误
                self._record_channel_error(e)
                
                # 特殊处理 CANCELLED 错误的日志
                if e.code() == grpc.StatusCode.CANCELLED:
                    channel_state = None
                    if self.channel:
                        try:
                            channel_state = self.channel._channel.check_connectivity_state(False)
                        except:
                            channel_state = "UNKNOWN"
                    
                    logger.warning(
                        f"⚠️ CANCELLED error detected, channel state: {channel_state}",
                        extra={
                            "log_type": "cancelled_debug",
                            "request_id": context.get('request_id'),
                            "data": {
                                "channel_state": str(channel_state) if channel_state else "NO_CHANNEL",
                                "channel_error_count": self._channel_error_count,
                                "time_since_last_error": time.time() - self._last_channel_error_time if self._last_channel_error_time else None,
                                "channel_healthy": self._is_channel_healthy(),
                                "debug_string": e.debug_error_string() if hasattr(e, 'debug_error_string') else ""
                            }
                        }
                    )
                
                # 检查是否应该尝试快速降级
                should_try_fallback = self._should_try_fallback(e.code(), attempt)
                
                if should_try_fallback:
                    # 尝试快速降级到HTTP
                    logger.warning(
                        f"🚀 Fast fallback triggered for {e.code().name} after {attempt + 1} attempts",
                        extra={
                            "log_type": "fast_fallback",
                            "request_id": context.get('request_id'),
                            "data": {
                                "error_code": e.code().name,
                                "attempt": attempt,
                                "fallback_reason": "immediate" if e.code() in self.immediate_fallback_errors else "after_retries"
                            }
                        }
                    )
                    
                    try:
                        # 从 kwargs 中提取降级所需的参数
                        fallback_kwargs = kwargs.copy()
                        
                        # 如果是 _invoke_request，需要提取 model_request
                        if func.__name__ == '_invoke_request' and len(args) >= 3:
                            # args 结构: (request, metadata, invoke_timeout)
                            # 需要从原始参数中恢复 model_request
                            if hasattr(self, '_current_model_request'):
                                model_request = self._current_model_request
                                origin_request_id = getattr(self, '_current_origin_request_id', None)
                                timeout = args[2] if len(args) > 2 else None
                                request_id = context.get('request_id')
                                
                                # 尝试HTTP降级
                                result = self._invoke_http_fallback(model_request, timeout, request_id, origin_request_id)
                        # 如果是 BatchInvoke，需要使用批量降级
                        elif func.__name__ == 'BatchInvoke' and hasattr(self, '_current_batch_request'):
                            batch_request = self._current_batch_request
                            origin_request_id = getattr(self, '_current_origin_request_id', None)
                            timeout = fallback_kwargs.get('timeout')
                            request_id = context.get('request_id')
                            
                            # 尝试批量HTTP降级
                            result = self._invoke_batch_http_fallback(batch_request, timeout, request_id, origin_request_id)
                        else:
                            # 其他情况，无法处理降级
                            raise ValueError(f"Unable to perform HTTP fallback for {func.__name__}")
                                
                        logger.info(
                            f"✅ Fast fallback to HTTP succeeded",
                            extra={
                                "log_type": "fast_fallback_success",
                                "request_id": request_id,
                                "data": {
                                    "grpc_attempts": attempt + 1,
                                    "fallback_duration": time.time() - method_start_time
                                }
                            }
                        )
                        
                        return result
                    except Exception as fallback_error:
                        # 降级失败，记录日志但继续原有重试逻辑
                        logger.warning(
                            f"⚠️ Fast fallback to HTTP failed: {str(fallback_error)}",
                            extra={
                                "log_type": "fast_fallback_failed",
                                "request_id": context.get('request_id'),
                                "data": {
                                    "fallback_error": str(fallback_error),
                                    "will_continue_grpc_retry": should_retry and attempt < self.max_retries
                                }
                            }
                        )
                
                if not should_retry or attempt >= self.max_retries:
                    # 不可重试或已达到最大重试次数
                    context['duration'] = current_duration
                    
                    # 记录最终失败日志
                    log_data = {
                        "log_type": "info",
                        "request_id": context.get('request_id'),
                        "data": {
                            "error_code": e.code().name if e.code() else 'UNKNOWN',
                            "error_details": e.details() if hasattr(e, 'details') else '',
                            "retry_count": attempt,
                            "max_retries": self.max_retries,
                            "method": context.get('method', 'unknown'),
                            "final_failure": True
                        },
                        "duration": current_duration
                    }
                    error_detail = f" - {e.details()}" if e.details() else ""
                    logger.warning(
                        f"⚠️ Final attempt {attempt + 1}/{self.max_retries + 1} failed: {e.code()}{error_detail} (no more retries)",
                        extra=log_data
                    )
                    
                    last_exception = self.error_handler.handle_error(e, context)
                    break
                
                # 可以重试，记录重试日志
                log_data = {
                    "log_type": "info",
                    "request_id": context.get('request_id'),
                    "data": {
                        "error_code": e.code().name if e.code() else 'UNKNOWN',
                        "error_details": e.details() if hasattr(e, 'details') else '',
                        "retry_count": attempt,
                        "max_retries": self.max_retries,
                        "method": context.get('method', 'unknown'),
                        "will_retry": True,
                        "fallback_attempted": should_try_fallback
                    },
                    "duration": current_duration
                }
                error_detail = f" - {e.details()}" if e.details() else ""
                logger.warning(
                    f"🔄 Attempt {attempt + 1}/{self.max_retries + 1} failed: {e.code()}{error_detail} (will retry)",
                    extra=log_data
                )

                # 执行退避等待
                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt, e.code())
                    time.sleep(delay)
                
                # 保存异常，以备后续使用
                last_exception = e

            except Exception as e:
                # 非 gRPC 错误，直接包装抛出
                context['retry_count'] = attempt
                last_exception = TamarModelException(str(e))
                break

        # 抛出最后的异常
        if last_exception:
            raise last_exception
        else:
            raise TamarModelException("Unknown error occurred")

    def _should_retry(self, error: grpc.RpcError, attempt: int) -> bool:
        """
        判断是否应该重试
        
        Args:
            error: gRPC错误
            attempt: 当前重试次数
            
        Returns:
            bool: 是否应该重试
        """
        error_code = error.code()
        from .exceptions import get_retry_policy, ErrorContext
        policy = get_retry_policy(error_code)
        
        # 先检查错误级别的 max_attempts 配置
        # max_attempts 表示最大重试次数（不包括初始请求）
        error_max_attempts = policy.get('max_attempts', self.max_retries)
        if attempt >= error_max_attempts:
            return False
            
        # 再检查全局的 max_retries
        if attempt >= self.max_retries:
            return False
        
        retryable = policy.get('retryable', False)
        
        if retryable == False:
            return False
        elif retryable == True:
            return True
        elif retryable == 'conditional':
            # 条件重试，特殊处理
            if error_code == grpc.StatusCode.CANCELLED:
                # 检查是否是网络中断导致的取消
                context = {'method': 'unknown', 'client_version': 'sync'}
                error_context = ErrorContext(error, context)
                return error_context.is_network_cancelled()
            else:
                return self._check_error_details_for_retry(error)
        
        return False
    
    def _check_error_details_for_retry(self, error: grpc.RpcError) -> bool:
        """
        检查错误详情决定是否重试
        
        Args:
            error: gRPC错误
            
        Returns:
            bool: 是否应该重试
        """
        error_message = error.details().lower() if error.details() else ""
        
        # 可重试的错误模式
        retryable_patterns = [
            'temporary', 'timeout', 'unavailable', 
            'connection', 'network', 'try again'
        ]
        
        for pattern in retryable_patterns:
            if pattern in error_message:
                return True
                
        return False

    def _calculate_backoff(self, attempt: int, error_code: grpc.StatusCode = None) -> float:
        """
        计算退避时间，支持不同的退避策略
        
        Args:
            attempt: 当前重试次数
            error_code: gRPC错误码，用于确定退避策略
        """
        max_delay = 60.0
        base_delay = self.retry_delay
        
        # 获取错误的重试策略
        if error_code:
            from .exceptions import get_retry_policy
            policy = get_retry_policy(error_code)
            backoff_type = policy.get('backoff', 'exponential')
            use_jitter = policy.get('jitter', False)
        else:
            backoff_type = 'exponential'
            use_jitter = False
        
        # 根据退避类型计算延迟
        if backoff_type == 'linear':
            # 线性退避：delay * (attempt + 1)
            delay = min(base_delay * (attempt + 1), max_delay)
        else:
            # 指数退避：delay * 2^attempt
            delay = min(base_delay * (2 ** attempt), max_delay)
        
        # 添加抖动
        if use_jitter:
            jitter_factor = 0.2  # 增加抖动范围，减少竞争
            jitter = random.uniform(0, delay * jitter_factor)
            delay += jitter
        else:
            # 默认的小量抖动，避免完全同步
            jitter_factor = 0.05
            jitter = random.uniform(0, delay * jitter_factor)
            delay += jitter
            
        return delay

    def _retry_request_stream(self, func, *args, **kwargs):
        """
        流式请求的重试逻辑（同步版本）
        
        对于流式响应，需要特殊的重试处理，因为流不能简单地重新执行。
        
        Args:
            func: 生成流的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Yields:
            流式响应的每个元素
        """
        # 记录方法开始时间
        method_start_time = time.time()
        
        # 从kwargs中提取request_id（如果有的话），然后移除它
        request_id = kwargs.pop('request_id', None) or get_request_id()
        
        last_exception = None
        context = {
            'method': 'stream',
            'client_version': 'sync',
            'request_id': request_id,
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                context['retry_count'] = attempt
                # 尝试创建流
                for item in func(*args, **kwargs):
                    yield item
                return
                
            except grpc.RpcError as e:
                # 使用智能重试判断
                context['retry_count'] = attempt
                
                # 计算当前的耗时
                current_duration = time.time() - method_start_time
                
                # 判断是否应该重试
                should_retry = self._should_retry(e, attempt)
                if not should_retry or attempt >= self.max_retries:
                    # 不重试或已达到最大重试次数
                    log_data = {
                        "log_type": "info",
                        "request_id": context.get('request_id'),
                        "data": {
                            "error_code": e.code().name if e.code() else 'UNKNOWN',
                            "error_details": e.details() if hasattr(e, 'details') else '',
                            "retry_count": attempt,
                            "max_retries": self.max_retries,
                            "method": "stream",
                            "will_retry": False
                        },
                        "duration": current_duration
                    }
                    error_detail = f" - {e.details()}" if e.details() else ""
                    logger.error(
                        f"❌ Stream failed: {e.code()}{error_detail} (no retry)",
                        extra=log_data
                    )
                    context['duration'] = current_duration
                    last_exception = self.error_handler.handle_error(e, context)
                    break
                
                # 记录重试日志
                log_data = {
                    "log_type": "info",
                    "request_id": context.get('request_id'),
                    "data": {
                        "error_code": e.code().name if e.code() else 'UNKNOWN',
                        "error_details": e.details() if hasattr(e, 'details') else '',
                        "retry_count": attempt,
                        "max_retries": self.max_retries,
                        "method": "stream"
                    },
                    "duration": current_duration
                }
                error_detail = f" - {e.details()}" if e.details() else ""
                logger.warning(
                    f"🔄 Stream attempt {attempt + 1}/{self.max_retries + 1} failed: {e.code()}{error_detail} (will retry)",
                    extra=log_data
                )
                
                # 执行退避等待
                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt, e.code())
                    time.sleep(delay)
                    
                last_exception = e
                
            except Exception as e:
                context['retry_count'] = attempt
                raise TamarModelException(str(e)) from e
        
        if last_exception:
            if isinstance(last_exception, TamarModelException):
                raise last_exception
            else:
                raise self.error_handler.handle_error(last_exception, context)
        else:
            raise TamarModelException("Unknown streaming error occurred")

    def _stream(self, request, metadata, invoke_timeout, request_id=None, origin_request_id=None) -> Iterator[ModelResponse]:
        """
        处理流式响应
        
        Args:
            request: gRPC 请求对象
            metadata: 请求元数据（为了兼容性保留，但会被忽略）
            invoke_timeout: 总体超时时间
            request_id: 请求ID
            origin_request_id: 原始请求ID
            
        Yields:
            ModelResponse: 流式响应的每个数据块
            
        Raises:
            TimeoutError: 当等待下一个数据块超时时
        """
        # 每次调用时重新生成metadata，确保JWT token是最新的
        fresh_metadata = self._build_auth_metadata(
            request_id or get_request_id(), 
            origin_request_id
        )
        import threading
        import queue
        
        # 创建队列用于线程间通信
        response_queue = queue.Queue()
        exception_queue = queue.Queue()
        
        def fetch_responses():
            """在单独线程中获取流式响应"""
            try:
                for response in self.stub.Invoke(request, metadata=fresh_metadata, timeout=invoke_timeout):
                    response_queue.put(response)
                response_queue.put(None)  # 标记流结束
            except Exception as e:
                exception_queue.put(e)
                response_queue.put(None)
        
        # 启动响应获取线程
        fetch_thread = threading.Thread(target=fetch_responses)
        fetch_thread.daemon = True
        fetch_thread.start()
        
        chunk_timeout = 30.0  # 单个数据块的超时时间
        
        while True:
            # 检查是否有异常
            if not exception_queue.empty():
                raise exception_queue.get()
            
            try:
                # 等待下一个响应，带超时
                response = response_queue.get(timeout=chunk_timeout)
                
                if response is None:
                    # 流结束
                    break
                    
                yield ResponseHandler.build_model_response(response)
                
            except queue.Empty:
                raise TimeoutError(f"流式响应在等待下一个数据块时超时 ({chunk_timeout}s)")

    def _stream_with_logging(self, request, metadata, invoke_timeout, start_time, model_request, request_id=None, origin_request_id=None) -> Iterator[
        ModelResponse]:
        """流式响应的包装器，用于记录完整的响应日志并处理重试"""
        total_content = ""
        final_usage = None
        error_occurred = None
        chunk_count = 0

        try:
            for response in self._stream(request, metadata, invoke_timeout, request_id, origin_request_id):
                chunk_count += 1
                if response.content:
                    total_content += response.content
                if response.usage:
                    final_usage = response.usage
                if response.error:
                    error_occurred = response.error
                yield response

            # 流式响应完成，记录日志
            duration = time.time() - start_time
            if error_occurred:
                # 流式响应中包含错误
                logger.warning(
                    f"⚠️ Stream completed with errors | chunks: {chunk_count}",
                    extra={
                        "log_type": "response",
                        "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                        "duration": duration,
                        "data": ResponseHandler.build_log_data(
                            model_request,
                            stream_stats={
                                "chunks_count": chunk_count,
                                "total_length": len(total_content),
                                "usage": final_usage,
                                "error": error_occurred
                            }
                        )
                    }
                )
            else:
                # 流式响应成功完成
                logger.info(
                    f"✅ Stream completed successfully | chunks: {chunk_count}",
                    extra={
                        "log_type": "response",
                        "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                        "duration": duration,
                        "data": ResponseHandler.build_log_data(
                            model_request,
                            stream_stats={
                                "chunks_count": chunk_count,
                                "total_length": len(total_content),
                                "usage": final_usage
                            }
                        )
                    }
                )
        except Exception as e:
            # 流式响应出错，记录错误日志
            duration = time.time() - start_time
            logger.error(
                f"❌ Stream failed after {chunk_count} chunks: {str(e)}",
                exc_info=True,
                extra={
                    "log_type": "response",
                    "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                    "duration": duration,
                    "data": ResponseHandler.build_log_data(
                        model_request,
                        error=e,
                        stream_stats={
                            "chunks_count": chunk_count,
                            "partial_content_length": len(total_content)
                        }
                    )
                }
            )
            raise

    def _invoke_request(self, request, metadata, invoke_timeout, request_id=None, origin_request_id=None):
        """执行单个非流式请求
        
        Args:
            request: gRPC请求对象
            metadata: 请求元数据（为了兼容性保留，但会被忽略）
            invoke_timeout: 请求超时时间
            request_id: 请求ID
            origin_request_id: 原始请求ID
        """
        # 每次调用时重新生成metadata，确保JWT token是最新的
        fresh_metadata = self._build_auth_metadata(
            request_id or get_request_id(), 
            origin_request_id
        )
        response = self.stub.Invoke(request, metadata=fresh_metadata, timeout=invoke_timeout)
        for response in response:
            return ResponseHandler.build_model_response(response)

    def invoke(self, model_request: ModelRequest, timeout: Optional[float] = None, request_id: Optional[str] = None) -> \
            Union[ModelResponse, Iterator[ModelResponse]]:
        """
       通用调用模型方法。

        Args:
            model_request: ModelRequest 对象，包含请求参数。
            timeout: Optional[float]
            request_id: Optional[str]
        Yields:
            ModelResponse: 支持流式或非流式的模型响应

        Raises:
            ValidationError: 输入验证失败。
            ConnectionError: 连接服务端失败。
        """
        # 如果启用了熔断且熔断器打开，直接走 HTTP
        if self.resilient_enabled and self.circuit_breaker and self.circuit_breaker.is_open:
            if self.http_fallback_url:
                logger.warning("🔻 Circuit breaker is OPEN, using HTTP fallback")
                # 在这里还没有计算origin_request_id，所以先计算
                temp_origin_request_id = None
                temp_request_id = request_id
                if request_id:
                    temp_request_id, temp_origin_request_id = self._request_id_manager.get_composite_id(request_id)
                return self._invoke_http_fallback(model_request, timeout, temp_request_id, temp_origin_request_id)
                
        self._ensure_initialized()

        if not self.default_payload:
            self.default_payload = {
                "org_id": model_request.user_context.org_id or "",
                "user_id": model_request.user_context.user_id or ""
            }

        # 处理 request_id
        origin_request_id = None
        if request_id:
            # 用户提供了 request_id，生成组合 ID
            request_id, origin_request_id = self._request_id_manager.get_composite_id(request_id)
        else:
            # 没有提供，生成新的
            request_id = generate_request_id()
            
        set_request_id(request_id)
        if origin_request_id:
            set_origin_request_id(origin_request_id)
        metadata = self._build_auth_metadata(request_id, origin_request_id)

        # 构建日志数据
        log_data = ResponseHandler.build_log_data(model_request)
        if origin_request_id:
            log_data['origin_request_id'] = origin_request_id

        # 记录开始日志
        start_time = time.time()
        logger.info(
            f"🔵 Request Start | request_id: {request_id} | provider: {model_request.provider} | invoke_type: {model_request.invoke_type}",
            extra={
                "log_type": "request",
                "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                "data": log_data
            })

        try:
            # 构建 gRPC 请求
            request = RequestBuilder.build_single_request(model_request)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"❌ Request build failed: {str(e)}",
                exc_info=True,
                extra={
                    "log_type": "response",
                    "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                    "duration": duration,
                    "data": {
                        "provider": model_request.provider.value,
                        "invoke_type": model_request.invoke_type.value,
                        "model": getattr(model_request, 'model', None),
                        "error_type": "build_error",
                        "error_message": str(e)
                    }
                }
            )
            raise ValueError(f"构建请求失败: {str(e)}") from e

        try:
            invoke_timeout = timeout or self.default_invoke_timeout
            if model_request.stream:
                # 对于流式响应，使用重试包装器
                return self._retry_request_stream(
                    self._stream_with_logging,
                    request, metadata, invoke_timeout, start_time, model_request,
                    request_id=request_id, origin_request_id=origin_request_id
                )
            else:
                # 存储model_request和origin_request_id供重试方法使用
                self._current_model_request = model_request
                self._current_origin_request_id = origin_request_id
                try:
                    result = self._retry_request(self._invoke_request, request, metadata, invoke_timeout, request_id=request_id, origin_request_id=origin_request_id)
                finally:
                    # 清理临时存储
                    if hasattr(self, '_current_model_request'):
                        delattr(self, '_current_model_request')
                    if hasattr(self, '_current_origin_request_id'):
                        delattr(self, '_current_origin_request_id')

                # 记录非流式响应的成功日志
                duration = time.time() - start_time
                content_length = len(result.content) if result.content else 0
                
                # 构建响应日志数据
                response_log_data = ResponseHandler.build_log_data(model_request, result)
                if origin_request_id:
                    response_log_data['origin_request_id'] = origin_request_id
                    
                logger.info(
                    f"✅ Request completed | content_length: {content_length}",
                    extra={
                        "log_type": "response",
                        "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                        "duration": duration,
                        "data": response_log_data
                    }
                )
                
                # 记录成功（如果启用了熔断）
                if self.resilient_enabled and self.circuit_breaker:
                    self.circuit_breaker.record_success()
                    
                return result
                
        except (ConnectionError, grpc.RpcError) as e:
            duration = time.time() - start_time
            error_message = f"❌ Invoke gRPC failed: {str(e)}"
            
            # 构建错误日志数据
            error_log_data = ResponseHandler.build_log_data(model_request, error=e)
            if origin_request_id:
                error_log_data['origin_request_id'] = origin_request_id
                
            logger.error(error_message, exc_info=True,
                         extra={
                             "log_type": "response",
                             "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                             "duration": duration,
                             "data": error_log_data
                         })
            
            # 记录 channel 错误
            if isinstance(e, grpc.RpcError):
                self._record_channel_error(e)
            
            # 记录失败（如果启用了熔断）
            if self.resilient_enabled and self.circuit_breaker:
                # 将错误码传递给熔断器，用于智能失败统计
                error_code = e.code() if hasattr(e, 'code') else None
                self.circuit_breaker.record_failure(error_code)
            
            raise e
        except Exception as e:
            duration = time.time() - start_time
            error_message = f"❌ Invoke other error: {str(e)}"
            logger.error(error_message, exc_info=True,
                         extra={
                             "log_type": "response",
                             "uri": f"/invoke/{model_request.provider.value}/{model_request.invoke_type.value}",
                             "duration": duration,
                             "data": ResponseHandler.build_log_data(
                                 model_request,
                                 error=e
                             )
                         })
            raise e

    def invoke_batch(self, batch_request_model: BatchModelRequest, timeout: Optional[float] = None,
                     request_id: Optional[str] = None) -> BatchModelResponse:
        """
        批量模型调用接口

        Args:
            batch_request_model: 多条 BatchModelRequest 输入
            timeout: 调用超时，单位秒
            request_id: 请求id
        Returns:
            BatchModelResponse: 批量请求的结果
        """
        # 如果启用了熔断且熔断器打开，直接走 HTTP
        if self.resilient_enabled and self.circuit_breaker and self.circuit_breaker.is_open:
            if self.http_fallback_url:
                logger.warning("🔻 Circuit breaker is OPEN, using HTTP fallback for batch request")
                # 在这里还没有计算origin_request_id，所以先计算
                temp_origin_request_id = None
                temp_request_id = request_id
                if request_id:
                    temp_request_id, temp_origin_request_id = self._request_id_manager.get_composite_id(request_id)
                return self._invoke_batch_http_fallback(batch_request_model, timeout, temp_request_id, temp_origin_request_id)
                
        self._ensure_initialized()

        if not self.default_payload:
            self.default_payload = {
                "org_id": batch_request_model.user_context.org_id or "",
                "user_id": batch_request_model.user_context.user_id or ""
            }

        # 处理 request_id
        origin_request_id = None
        if request_id:
            # 用户提供了 request_id，生成组合 ID
            request_id, origin_request_id = self._request_id_manager.get_composite_id(request_id)
        else:
            # 没有提供，生成新的
            request_id = generate_request_id()
            
        set_request_id(request_id)
        if origin_request_id:
            set_origin_request_id(origin_request_id)
        metadata = self._build_auth_metadata(request_id, origin_request_id)

        # 构建日志数据
        batch_log_data = {
            "batch_size": len(batch_request_model.items),
            "org_id": batch_request_model.user_context.org_id,
            "user_id": batch_request_model.user_context.user_id,
            "client_type": batch_request_model.user_context.client_type
        }
        if origin_request_id:
            batch_log_data['origin_request_id'] = origin_request_id

        # 记录开始日志
        start_time = time.time()
        logger.info(
            f"🔵 Batch Request Start | request_id: {request_id} | batch_size: {len(batch_request_model.items)}",
            extra={
                "log_type": "request",
                "uri": "/batch_invoke",
                "data": batch_log_data
            })

        try:
            # 构建批量请求
            batch_request = RequestBuilder.build_batch_request(batch_request_model)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"❌ Batch request build failed: {str(e)}",
                exc_info=True,
                extra={
                    "log_type": "response",
                    "uri": "/batch_invoke",
                    "duration": duration,
                    "data": {
                        "batch_size": len(batch_request_model.items),
                        "error_type": "build_error",
                        "error_message": str(e)
                    }
                }
            )
            raise ValueError(f"构建批量请求失败: {str(e)}") from e

        try:
            invoke_timeout = timeout or self.default_invoke_timeout
            
            # 保存批量请求信息用于降级
            self._current_batch_request = batch_request_model
            self._current_origin_request_id = origin_request_id
            
            batch_response = self._retry_request(
                self.stub.BatchInvoke,
                batch_request,
                metadata=metadata,
                timeout=invoke_timeout,
                request_id=request_id
            )

            # 构建响应对象
            result = ResponseHandler.build_batch_response(batch_response)

            # 记录成功日志
            duration = time.time() - start_time
            logger.info(
                f"✅ Batch Request completed | batch_size: {len(result.responses)}",
                extra={
                    "log_type": "response",
                    "uri": "/batch_invoke",
                    "duration": duration,
                    "data": {
                        "batch_size": len(result.responses),
                        "success_count": sum(1 for item in result.responses if not item.error),
                        "error_count": sum(1 for item in result.responses if item.error)
                    }
                })

            return result

        except grpc.RpcError as e:
            duration = time.time() - start_time
            error_message = f"❌ Batch invoke gRPC failed: {str(e)}"
            logger.error(error_message, exc_info=True,
                         extra={
                             "log_type": "response",
                             "uri": "/batch_invoke",
                             "duration": duration,
                             "data": {
                                 "error_type": "grpc_error",
                                 "error_code": str(e.code()) if hasattr(e, 'code') else None,
                                 "batch_size": len(batch_request_model.items)
                             }
                         })
            
            # 记录失败（如果启用了熔断）
            if self.resilient_enabled and self.circuit_breaker:
                # 将错误码传递给熔断器，用于智能失败统计
                error_code = e.code() if hasattr(e, 'code') else None
                self.circuit_breaker.record_failure(error_code)
            
            raise e
        except Exception as e:
            duration = time.time() - start_time
            error_message = f"❌ Batch invoke other error: {str(e)}"
            logger.error(error_message, exc_info=True,
                         extra={
                             "log_type": "response",
                             "uri": "/batch_invoke",
                             "duration": duration,
                             "data": {
                                 "error_type": "other_error",
                                 "batch_size": len(batch_request_model.items)
                             }
                         })
            raise e