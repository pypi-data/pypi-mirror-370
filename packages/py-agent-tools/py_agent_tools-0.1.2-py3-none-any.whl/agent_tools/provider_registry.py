"""
Provider registry for managing agent and credential pool classes.
This module provides a registry pattern to avoid circular imports.
"""

from typing import Type

import json5

from agent_tools._log import log
from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolProtocol
from agent_tools.provider_config import AccountCredential, ProviderConfig
from agent_tools.settings import agent_settings


def read_account_credentials(provider: str) -> list[AccountCredential]:
    """
    Read account credentials from file.
    """
    provider_config_path = agent_settings.model_provider_config_dir / f"{provider}.jsonc"
    try:
        if not provider_config_path.exists():
            log.warning(f"{provider} credentials file not found at {provider_config_path}")
            return []
        with provider_config_path.open() as f:
            data = json5.load(f)
            if isinstance(data, list):
                return [AccountCredential(**cred) for cred in data]
            else:
                provider_config = ProviderConfig.model_validate(data)
                for account in provider_config.accounts:
                    if not account.supported_models:
                        account.supported_models = provider_config.default_models
                return provider_config.accounts
    except FileNotFoundError as e:
        log.warning(f"{e}")
        return []
    except Exception as e:
        log.error(f"Invalid JSON5 in {provider_config_path}: {e}")
        return []


class ProviderRegistry:
    """Registry for provider classes to avoid circular imports."""

    _agent_tools: dict[str, Type[AgentBase]] = {}
    _credential_pools: dict[str, Type[CredentialPoolProtocol]] = {}
    _model_names: dict[str, Type[ModelNameBase]] = {}
    _account_credentials: dict[str, list[AccountCredential]] = {}

    @classmethod
    def _register_agent_tool_cls(cls, provider: str, agent_cls: Type[AgentBase]) -> None:
        """Register an agent class for a provider."""
        cls._agent_tools[provider] = agent_cls

    @classmethod
    def _register_credential_pool_cls(
        cls, provider: str, pool_cls: Type[CredentialPoolProtocol]
    ) -> None:
        """Register a credential pool class for a provider."""
        cls._credential_pools[provider] = pool_cls

    @classmethod
    def _register_model_name_enum(cls, provider: str, model_names_cls: Type[ModelNameBase]) -> None:
        """Register a model names class for a provider."""
        cls._model_names[provider] = model_names_cls

    @classmethod
    def _register_account_credentials(cls, provider: str) -> None:
        """Register a list of account credentials for a provider."""
        cls._account_credentials[provider] = read_account_credentials(provider)

    @classmethod
    def register_agent_tool(
        cls,
        provider: str,
        agent_cls: Type[AgentBase],
        pool_cls: Type[CredentialPoolProtocol],
        model_names_cls: Type[ModelNameBase],
    ) -> None:
        """Register an agent class for a provider."""
        cls._register_agent_tool_cls(provider, agent_cls)
        cls._register_credential_pool_cls(provider, pool_cls)
        cls._register_model_name_enum(provider, model_names_cls)
        cls._register_account_credentials(provider)

    @classmethod
    def register_credential_pool(
        cls, provider: str, pool_cls: Type[CredentialPoolProtocol]
    ) -> None:
        """Register a credential pool class for a provider."""
        cls._register_credential_pool_cls(provider, pool_cls)

    @classmethod
    def get_agent_tool_cls(cls, provider: str) -> Type[AgentBase]:
        """Get agent class for a provider."""
        if provider not in cls._agent_tools:
            raise ValueError(f"Agent not registered for provider: {provider}")
        return cls._agent_tools[provider]

    @classmethod
    def get_credential_pool_cls(cls, provider: str) -> Type[CredentialPoolProtocol]:
        """Get credential pool class for a provider."""
        if provider not in cls._credential_pools:
            raise ValueError(f"Credential pool not registered for provider: {provider}")
        return cls._credential_pools[provider]

    @classmethod
    def get_model_name_enum(cls, provider: str) -> Type[ModelNameBase]:
        """Get model names class for a provider."""
        if provider not in cls._model_names:
            raise ValueError(f"Model names not registered for provider: {provider}")
        return cls._model_names[provider]

    @classmethod
    def get_account_credentials(cls, provider: str) -> list[AccountCredential]:
        """Get account credentials for a provider."""
        if provider not in cls._account_credentials:
            raise ValueError(f"Account credentials not registered for provider: {provider}")
        return cls._account_credentials[provider]

    @classmethod
    def get_all_providers(cls) -> list[str]:
        """Get all registered providers."""
        return list(cls._agent_tools.keys())


# 注册函数，各个agent模块可以调用
def register_ark_provider():
    """Register ARK provider classes."""
    from agent_tools.ark_agent import ArkAgent, ArkCredentialPool, ArkModelName

    ProviderRegistry.register_agent_tool(
        "ark",
        ArkAgent,
        ArkCredentialPool,
        ArkModelName,
    )


def register_azure_provider():
    """Register Azure provider classes."""
    from agent_tools.azure_agent import AzureAgent, AzureCredentialPool, AzureModelName

    ProviderRegistry.register_agent_tool(
        "azure",
        AzureAgent,
        AzureCredentialPool,
        AzureModelName,
    )


def register_bailian_provider():
    """Register Bailian provider classes."""
    from agent_tools.bailian_agent import BailianAgent, BailianCredentialPool, BailianModelName

    ProviderRegistry.register_agent_tool(
        "bailian",
        BailianAgent,
        BailianCredentialPool,
        BailianModelName,
    )


def register_openai_provider():
    """Register OpenAI provider classes."""
    from agent_tools.openai_agent import OpenAIAgent, OpenAICredentialPool, OpenAIModelName

    ProviderRegistry.register_agent_tool(
        "openai",
        OpenAIAgent,
        OpenAICredentialPool,
        OpenAIModelName,
    )


def register_openai_ft_provider():
    """Register OpenAI Fine-tuning provider classes."""
    from agent_tools.openai_agent import OpenAIAgent
    from agent_tools.openai_ft_agent import (
        OpenAIFineTuningCredentialPool,
        OpenAIFineTuningModelName,
    )

    ProviderRegistry.register_agent_tool(
        "openai_ft",
        OpenAIAgent,
        OpenAIFineTuningCredentialPool,
        OpenAIFineTuningModelName,
    )


def register_laozhang_provider():
    """Register Laozhang provider classes."""
    from agent_tools.laozhang_agent import LaozhangAgent, LaozhangCredentialPool, LaozhangModelName

    ProviderRegistry.register_agent_tool(
        "laozhang",
        LaozhangAgent,
        LaozhangCredentialPool,
        LaozhangModelName,
    )


def register_laozhang_sgp_provider():
    """Register Laozhang Singapore provider classes."""
    from agent_tools.laozhang_agent import LaozhangAgent, LaozhangCredentialPool, LaozhangModelName

    ProviderRegistry.register_agent_tool(
        "laozhang_sgp",
        LaozhangAgent,
        LaozhangCredentialPool,
        LaozhangModelName,
    )


def register_model_relay_provider():
    """Register Model Relay provider classes."""
    from agent_tools.model_relay_agent import (
        ModelRelayAgent,
        ModelRelayCredentialPool,
        ModelRelayModelName,
    )

    ProviderRegistry.register_agent_tool(
        "model_relay",
        ModelRelayAgent,
        ModelRelayCredentialPool,
        ModelRelayModelName,
    )


def register_openai_pools_provider():
    """Register OpenAI Pools provider classes."""
    from agent_tools.openai_pools_agent import (
        OpenAIPoolsAgent,
        OpenAIPoolsCredentialPool,
        OpenAIPoolsModelName,
    )

    ProviderRegistry.register_agent_tool(
        "openai_pools",
        OpenAIPoolsAgent,
        OpenAIPoolsCredentialPool,
        OpenAIPoolsModelName,
    )


def register_providers(providers: list[str]):
    """Register available providers."""
    for provider in providers:
        if provider == "ark":
            register_ark_provider()
        elif provider == "azure":
            register_azure_provider()
        elif provider == "bailian":
            register_bailian_provider()
        elif provider == "openai":
            register_openai_provider()
        elif provider == "openai_ft":
            register_openai_ft_provider()
        elif provider == "laozhang":
            register_laozhang_provider()
        elif provider == "laozhang_sgp":
            register_laozhang_sgp_provider()
        elif provider == "model_relay":
            register_model_relay_provider()
        elif provider == "openai_pools":
            register_openai_pools_provider()
        else:
            log.warning(f"注册该 Agent 时未找到类的实现: {provider}，已忽略。")
