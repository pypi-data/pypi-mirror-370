"""
Base client class for Tamar Model Client

This module provides the base client class with shared initialization logic
and configuration management for both sync and async clients.
"""

import os
from typing import Optional
from abc import ABC, abstractmethod

from ..auth import JWTAuthHandler
from ..error_handler import GrpcErrorHandler, ErrorRecoveryStrategy
from .logging_setup import MAX_MESSAGE_LENGTH, get_protected_logger


class BaseClient(ABC):
    """
    基础客户端抽象类
    
    提供同步和异步客户端的共享功能：
    - 配置管理
    - 认证设置
    - 连接选项构建
    - 错误处理器初始化
    """

    def __init__(
            self,
            server_address: Optional[str] = None,
            jwt_secret_key: Optional[str] = None,
            jwt_token: Optional[str] = None,
            default_payload: Optional[dict] = None,
            token_expires_in: int = 3600,
            max_retries: Optional[int] = None,
            retry_delay: Optional[float] = None,
            logger_name: str = None,
    ):
        """
        初始化基础客户端
        
        Args:
            server_address: gRPC 服务器地址，格式为 "host:port"
            jwt_secret_key: JWT 签名密钥，用于生成认证令牌
            jwt_token: 预生成的 JWT 令牌（可选）
            default_payload: JWT 令牌的默认载荷
            token_expires_in: JWT 令牌过期时间（秒）
            max_retries: 最大重试次数（默认从环境变量读取）
            retry_delay: 初始重试延迟（秒，默认从环境变量读取）
            logger_name: 日志记录器名称
            
        Raises:
            ValueError: 当服务器地址未提供时
        """
        # === 服务端地址配置 ===
        self.server_address = server_address or os.getenv("MODEL_MANAGER_SERVER_ADDRESS")
        if not self.server_address:
            raise ValueError("Server address must be provided via argument or environment variable.")

        # 默认调用超时时间
        self.default_invoke_timeout = float(os.getenv("MODEL_MANAGER_SERVER_INVOKE_TIMEOUT", 30.0))

        # === JWT 认证配置 ===
        self.jwt_secret_key = jwt_secret_key or os.getenv("MODEL_MANAGER_SERVER_JWT_SECRET_KEY")
        self.jwt_handler = JWTAuthHandler(self.jwt_secret_key) if self.jwt_secret_key else None
        self.jwt_token = jwt_token  # 用户传入的预生成 Token（可选）
        self.default_payload = default_payload
        self.token_expires_in = token_expires_in

        # === TLS/Authority 配置 ===
        self.use_tls = os.getenv("MODEL_MANAGER_SERVER_GRPC_USE_TLS", "true").lower() == "true"
        self.default_authority = os.getenv("MODEL_MANAGER_SERVER_GRPC_DEFAULT_AUTHORITY")

        # === 重试配置 ===
        self.max_retries = max_retries if max_retries is not None else int(
            os.getenv("MODEL_MANAGER_SERVER_GRPC_MAX_RETRIES", 6))
        self.retry_delay = retry_delay if retry_delay is not None else float(
            os.getenv("MODEL_MANAGER_SERVER_GRPC_RETRY_DELAY", 1.0))

        # === 日志配置 ===
        self.logger = get_protected_logger(logger_name or __name__)

        # === 错误处理器 ===
        self.error_handler = GrpcErrorHandler(self.logger)
        self.recovery_strategy = ErrorRecoveryStrategy(self)

        # === 连接状态 ===
        self._closed = False

        # === 熔断降级配置 ===
        self._init_resilient_features()

        # === 快速降级配置 ===
        self._init_fast_fallback_config()

    def build_channel_options(self) -> list:
        """
        构建 gRPC 通道选项
        
        Returns:
            list: gRPC 通道配置选项列表
            
        包含的配置：
        - 消息大小限制
        - Keepalive 设置（30秒ping间隔，10秒超时）
        - 连接生命周期管理（1小时最大连接时间）
        - 性能优化选项（带宽探测、内置重试）
        """
        options = [
            # 消息大小限制
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),

            # Keepalive 核心配置
            ('grpc.keepalive_time_ms', 30000),  # 30秒发送一次 keepalive ping
            ('grpc.keepalive_timeout_ms', 10000),  # ping 响应超时时间 10秒
            ('grpc.keepalive_permit_without_calls', True),  # 空闲时也发送 keepalive
            ('grpc.http2.max_pings_without_data', 2),  # 无数据时最大 ping 次数

            # 连接管理增强配置
            ('grpc.http2.min_time_between_pings_ms', 10000),  # ping 最小间隔 10秒
            ('grpc.http2.max_connection_idle_ms', 300000),  # 最大空闲时间 5分钟
            ('grpc.http2.max_connection_age_ms', 3600000),  # 连接最大生存时间 1小时
            ('grpc.http2.max_connection_age_grace_ms', 5000),  # 优雅关闭时间 5秒

            # 性能相关配置
            ('grpc.http2.bdp_probe', 1),  # 启用带宽延迟探测
            ('grpc.enable_retries', 1),  # 启用内置重试

            # 启用连接池配置（如果 gRPC 客户端支持）
            ('grpc.keepalive_time_ms', 30000),  # 保持活跃的连接时间（30秒）
            ('grpc.keepalive_timeout_ms', 10000),  # ping 响应超时时间（10秒）
            ('grpc.max_connection_idle_ms', 300000),  # 连接最大空闲时间（5分钟）

            # 设置资源配额
            ('grpc.resource_quota_size', 1048576000),  # 设置资源配额为1GB

            # 启用负载均衡配置
            ('grpc.lb_policy_name', 'round_robin'), # 设置负载均衡策略为 round_robin（轮询）
        ]

        if self.default_authority:
            options.append(("grpc.default_authority", self.default_authority))

        return options

    def _build_auth_metadata(self, request_id: str, origin_request_id: Optional[str] = None) -> list:
        """
        构建认证元数据
        
        为每个请求构建包含认证信息和请求ID的gRPC元数据。
        JWT令牌会在每次请求时重新生成以确保有效性。
        
        Args:
            request_id: 当前请求的唯一标识符
            origin_request_id: 原始请求ID（可选）
            
        Returns:
            list: gRPC元数据列表，包含请求ID和认证令牌
        """
        metadata = [("x-request-id", request_id)]  # 将 request_id 添加到 headers

        # 如果有原始请求ID，也添加到 headers
        if origin_request_id:
            metadata.append(("x-origin-request-id", origin_request_id))

        if self.jwt_handler:
            # 检查token是否即将过期，如果是则刷新
            if self.jwt_handler.is_token_expiring_soon():
                self.jwt_token = self.jwt_handler.encode_token(
                    self.default_payload,
                    expires_in=self.token_expires_in
                )
            else:
                # 使用缓存的token
                cached_token = self.jwt_handler.get_cached_token()
                if cached_token:
                    self.jwt_token = cached_token
                else:
                    # 如果没有缓存，生成新token
                    self.jwt_token = self.jwt_handler.encode_token(
                        self.default_payload,
                        expires_in=self.token_expires_in
                    )
            
            metadata.append(("authorization", f"Bearer {self.jwt_token}"))
        elif self.jwt_token:
            # 使用用户提供的预生成token
            metadata.append(("authorization", f"Bearer {self.jwt_token}"))

        return metadata

    @abstractmethod
    def close(self):
        """关闭客户端连接（由子类实现）"""
        pass

    @abstractmethod
    def __enter__(self):
        """进入上下文管理器（由子类实现）"""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器（由子类实现）"""
        pass

    def _init_resilient_features(self):
        """初始化熔断降级特性"""
        # 是否启用熔断降级
        self.resilient_enabled = os.getenv('MODEL_CLIENT_RESILIENT_ENABLED', 'false').lower() == 'true'

        if self.resilient_enabled:
            # HTTP 降级地址
            self.http_fallback_url = os.getenv('MODEL_CLIENT_HTTP_FALLBACK_URL')

            if not self.http_fallback_url:
                self.logger.warning("🔶 Resilient mode enabled but MODEL_CLIENT_HTTP_FALLBACK_URL not set")
                self.resilient_enabled = False
                return

            # 初始化熔断器
            from ..circuit_breaker import CircuitBreaker
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=int(os.getenv('MODEL_CLIENT_CIRCUIT_BREAKER_THRESHOLD', '5')),
                recovery_timeout=int(os.getenv('MODEL_CLIENT_CIRCUIT_BREAKER_TIMEOUT', '60'))
            )

            # HTTP 客户端（延迟初始化）
            self._http_client = None
            self._http_session = None  # 异步客户端使用

            self.logger.info(
                "🛡️ Resilient mode enabled",
                extra={
                    "log_type": "info",
                    "data": {
                        "http_fallback_url": self.http_fallback_url,
                        "circuit_breaker_threshold": self.circuit_breaker.failure_threshold,
                        "circuit_breaker_timeout": self.circuit_breaker.recovery_timeout
                    }
                }
            )
        else:
            self.circuit_breaker = None
            self.http_fallback_url = None
            self._http_client = None
            self._http_session = None

    def get_resilient_metrics(self):
        """获取熔断降级指标"""
        if not self.resilient_enabled or not self.circuit_breaker:
            return None

        return {
            "enabled": self.resilient_enabled,
            "circuit_breaker": {
                "state": self.circuit_breaker.get_state(),
                "failure_count": self.circuit_breaker.failure_count,
                "last_failure_time": self.circuit_breaker.last_failure_time,
                "failure_threshold": self.circuit_breaker.failure_threshold,
                "recovery_timeout": self.circuit_breaker.recovery_timeout
            },
            "http_fallback_url": self.http_fallback_url
        }

    def _init_fast_fallback_config(self):
        """初始化快速降级配置"""
        import grpc

        # 是否启用快速降级
        self.fast_fallback_enabled = os.getenv('MODEL_CLIENT_FAST_FALLBACK_ENABLED', 'false').lower() == 'true'

        # 降级前的最大gRPC重试次数
        self.fallback_after_retries = int(os.getenv('MODEL_CLIENT_FALLBACK_AFTER_RETRIES', '1'))

        # 立即降级的错误码配置
        immediate_fallback_errors = os.getenv('MODEL_CLIENT_IMMEDIATE_FALLBACK_ERRORS',
                                              'UNAVAILABLE,DEADLINE_EXCEEDED,CANCELLED')
        self.immediate_fallback_errors = set()

        if immediate_fallback_errors:
            for error_name in immediate_fallback_errors.split(','):
                error_name = error_name.strip()
                if hasattr(grpc.StatusCode, error_name):
                    self.immediate_fallback_errors.add(getattr(grpc.StatusCode, error_name))

        # 永不降级的错误码
        never_fallback_errors = os.getenv('MODEL_CLIENT_NEVER_FALLBACK_ERRORS',
                                          'UNAUTHENTICATED,PERMISSION_DENIED,INVALID_ARGUMENT')
        self.never_fallback_errors = set()

        if never_fallback_errors:
            for error_name in never_fallback_errors.split(','):
                error_name = error_name.strip()
                if hasattr(grpc.StatusCode, error_name):
                    self.never_fallback_errors.add(getattr(grpc.StatusCode, error_name))

        if self.fast_fallback_enabled:
            self.logger.info(
                "🚀 Fast fallback enabled",
                extra={
                    "data": {
                        "fallback_after_retries": self.fallback_after_retries,
                        "immediate_fallback_errors": [e.name for e in self.immediate_fallback_errors],
                        "never_fallback_errors": [e.name for e in self.never_fallback_errors]
                    }
                }
            )

    def _should_try_fallback(self, error_code, attempt: int) -> bool:
        """
        判断是否应该尝试降级
        
        Args:
            error_code: gRPC错误码
            attempt: 当前重试次数
            
        Returns:
            bool: 是否应该尝试降级
        """
        # 未启用快速降级
        if not self.fast_fallback_enabled:
            return False

        # 未启用熔断降级功能
        if not self.resilient_enabled or not self.http_fallback_url:
            return False

        # 永不降级的错误类型
        if error_code in self.never_fallback_errors:
            return False

        # 立即降级的错误类型
        if error_code in self.immediate_fallback_errors:
            return True

        # 其他错误在达到重试次数后降级
        return attempt >= self.fallback_after_retries
