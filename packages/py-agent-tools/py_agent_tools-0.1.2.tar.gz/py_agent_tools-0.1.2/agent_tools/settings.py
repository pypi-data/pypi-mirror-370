"""
Settings for the agent_utils package.

This module contains the settings for the agent_utils package.

The settings are loaded from the environment variables.

"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from util_common.pydantic_util import show_settings_as_env


class AzureSettings(BaseSettings):
    """Azure OpenAI configuration settings."""

    model_config = SettingsConfigDict(env_prefix="AZURE_")


class ArkSettings(BaseSettings):
    """Ark configuration settings."""

    model_config = SettingsConfigDict(env_prefix="ARK_")


class OpenAISettings(BaseSettings):
    """OpenAI configuration settings."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_")


class OpenAIFineTuningSettings(BaseSettings):
    """OpenAI Fine-tuning configuration settings."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_FT_")


class VertexSettings(BaseSettings):
    """Google Vertex configuration settings."""

    model_config = SettingsConfigDict(env_prefix="VERTEX_")


class BailianSettings(BaseSettings):
    """Bailian configuration settings."""

    model_config = SettingsConfigDict(env_prefix="BAILIAN_")


class LaozhangSettings(BaseSettings):
    """Laozhang configuration settings."""

    model_config = SettingsConfigDict(env_prefix="LAOZHANG_")


class ModelRelaySettings(BaseSettings):
    """Model relay configuration settings."""

    model_config = SettingsConfigDict(env_prefix="MODEL_RELAY_")


class WechatAlertSettings(BaseSettings):
    """微信预警配置设置"""

    model_config = SettingsConfigDict(env_prefix="WECHAT_ALERT_")

    webhook_url: str = Field(
        default="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=17f331b6-f54f-4e78-a335-24ac60c54346",  # noqa
        description="企业微信群机器人webhook URL",
    )
    enabled: bool = Field(default=True, description="是否启用微信预警")
    alert_levels: list[str] = Field(default=["ERROR", "CRITICAL"], description="需要预警的异常级别")
    max_message_length: int = Field(default=2000, description="消息最大长度")
    retry_times: int = Field(default=3, description="发送失败重试次数")
    retry_delay: float = Field(default=1.0, description="重试间隔(秒)")


class AgentSettings(BaseSettings):
    """Main settings class that combines all settings."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="allow",
    )

    resource_root: Path = Field(
        default=Path("/mnt/ssd1/resource"),
        description="Root path for all resource files",
    )

    run_model_health_check: bool = Field(
        default=False,
        description="Whether to run health check",
    )

    default_model_health_check_interval: int = Field(
        default=3600,
        description="Interval in seconds for model health check",
    )

    # 微信预警配置
    wechat_alert: WechatAlertSettings = Field(default_factory=WechatAlertSettings)

    # 模型供应商 Agent 子类配置(如果有的话在子配置里添加)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    openai_ft: OpenAIFineTuningSettings = Field(default_factory=OpenAIFineTuningSettings)
    azure: AzureSettings = Field(default_factory=AzureSettings)
    ark: ArkSettings = Field(default_factory=ArkSettings)
    vertex: VertexSettings = Field(default_factory=VertexSettings)
    bailian: BailianSettings = Field(default_factory=BailianSettings)
    laozhang: LaozhangSettings = Field(default_factory=LaozhangSettings)
    model_relay: ModelRelaySettings = Field(default_factory=ModelRelaySettings)

    @property
    def model_provider_config_dir(self) -> Path:
        """
        Path to the model provider config files.
        """
        return self.resource_root / Path("credentials/model_providers")


agent_settings = AgentSettings()
show_settings_as_env(agent_settings)
