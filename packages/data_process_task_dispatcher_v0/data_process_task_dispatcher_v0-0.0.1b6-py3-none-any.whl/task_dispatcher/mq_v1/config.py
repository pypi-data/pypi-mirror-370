from dataclasses import dataclass
from typing import Optional, ClassVar
from threading import Lock


@dataclass
class MQConfig:
    """RabbitMQ configuration"""
    connection_url: str
    aggregator_url: Optional[str] = None  # Redis URL for message aggregation
    prefetch_count: int = 10
    message_ttl: int = 86400  # 1 day in seconds
    max_retries: int = 3  # 最大重试次数
    retry_delay: int = 1000  # 重试延迟(毫秒)
    enable_dlx: bool = True  # 是否启用死信交换机

    @classmethod
    def from_settings(cls, settings):
        """Create config from settings object"""
        return cls(
            connection_url=settings.rabbitmq.APP_MQ_CONNECTION_URL,
            aggregator_url=getattr(settings.rabbitmq, "APP_MQ_AGGREGATOR_URL", None),
            prefetch_count=getattr(settings.rabbitmq, "APP_MQ_PREFETCH_COUNT", 10),
            message_ttl=getattr(settings.rabbitmq, "APP_MQ_MESSAGE_TTL", 86400),
            max_retries=getattr(settings.rabbitmq, "APP_MQ_MAX_RETRIES", 3),
            retry_delay=getattr(settings.rabbitmq, "APP_MQ_RETRY_DELAY", 1000),
            enable_dlx=getattr(settings.rabbitmq, "APP_MQ_ENABLE_DLX", True),
        )


class ConfigurationManager:
    """全局配置管理器"""
    _instance = None
    _lock = Lock()
    _config: Optional[MQConfig] = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    @classmethod
    def init(cls, config: Optional[MQConfig] = None, settings=None):
        """
        初始化全局配置

        Args:
            config: MQConfig 实例，如果提供则直接使用
            settings: settings 对象，如果没有提供 config，则从 settings 创建配置

        Example:
            # 方式1：直接使用配置对象
            config = MQConfig(connection_url="amqp://localhost")
            ConfigurationManager.init(config=config)

            # 方式2：从 settings 初始化
            from your_project.settings import settings
            ConfigurationManager.init(settings=settings)
        """
        with cls._lock:
            if config:
                cls._config = config
            elif settings:
                cls._config = MQConfig.from_settings(settings)
            else:
                raise ValueError("Either config or settings must be provided")

    @classmethod
    def get_config(cls) -> MQConfig:
        """获取当前配置"""
        if cls._config is None:
            raise RuntimeError(
                "Configuration not initialized. Call ConfigurationManager.init() first"
            )
        return cls._config

    @classmethod
    def reset(cls):
        """重置配置（主要用于测试）"""
        with cls._lock:
            cls._config = None 