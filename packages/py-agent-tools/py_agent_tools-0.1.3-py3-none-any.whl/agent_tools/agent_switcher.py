from collections import defaultdict
from functools import cached_property

from pydantic import BaseModel

from agent_tools._log import log
from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, CredentialPoolProtocol
from agent_tools.provider_config import AccountCredential
from agent_tools.provider_registry import ProviderRegistry, register_providers


class ProviderMapping(BaseModel):
    provider: str
    agent_tool_cls: type[AgentBase]
    local_credential_pool_cls: type[CredentialPoolProtocol]
    model_name_enum: type[ModelNameBase]
    account_credentials: list[AccountCredential]


class AgentSwitcher:

    def __init__(self, providers: list[str], using_remote_credential_pools: bool = False):
        self.using_remote_credential_pools = using_remote_credential_pools
        self.available_providers: list[str] = providers
        self._credential_pools: defaultdict[str, dict[str, CredentialPoolProtocol]] = defaultdict(
            dict
        )
        self.provider_mappings = self._get_provider_mappings()

    def register_providers(self) -> None:
        """
        可以复写这个方法，实现自定义的 Agent 类，并添加注册逻辑。
        确保所有 providers 都已注册 (参考 provider_registry.py 中注册)。
        """
        register_providers(self.available_providers)

    def _get_provider_mappings(self) -> dict[str, ProviderMapping]:
        """
        获取所有已注册的 provider 的映射。
        """
        self.register_providers()
        mappings = {}
        for provider in self.available_providers:
            if provider in ProviderRegistry.get_all_providers():
                mappings[provider] = ProviderMapping(
                    provider=provider,
                    agent_tool_cls=ProviderRegistry.get_agent_tool_cls(provider),
                    local_credential_pool_cls=ProviderRegistry.get_credential_pool_cls(provider),
                    model_name_enum=ProviderRegistry.get_model_name_enum(provider),
                    account_credentials=ProviderRegistry.get_account_credentials(provider),
                )
        return mappings

    @cached_property
    def credential_pools(self) -> dict[str, dict[str, CredentialPoolProtocol]]:
        if self.using_remote_credential_pools:
            raise NotImplementedError("Remote credential pools are not implemented yet")
        else:
            providers = list(self._credential_pools.keys())
            for provider in providers:
                model_names = list(self._credential_pools[provider].keys())
                for model_name in model_names:
                    pool = self._credential_pools[provider][model_name]
                    if len(pool.get_model_credentials()) > 0:
                        pass
                    else:
                        if isinstance(pool, CredentialPoolBase):
                            pool.stop()
                        del self._credential_pools[provider][model_name]
            log.warning("当前帐号池支持以下模型:")
            for provider, pools in self._credential_pools.items():
                for model in pools.keys():
                    log.warning(f"provider: {provider}, model: {model}")
            return self._credential_pools

    def get_credential_pool(self, provider: str, model_name: str) -> CredentialPoolProtocol:
        """Get credential pool for a specific model."""
        if provider not in self.credential_pools:
            raise ValueError(f"Provider '{provider}' not found")
        if model_name not in self.credential_pools[provider]:
            raise ValueError(f"Model '{model_name}' not found for provider '{provider}'")
        return self.credential_pools[provider][model_name]

    def get_agent_cls(self, provider: str) -> type[AgentBase]:
        """Get agent for a specific model."""
        mapping = self.provider_mappings.get(provider, None)
        if mapping is None:
            raise ValueError(f"Provider '{provider}' not found")
        return mapping.agent_tool_cls

    async def start_all_pools(self, allowed_providers: list[str] | None = None):
        """Start all credential pools for health checking."""
        if allowed_providers is None:
            allowed_providers = list(self.provider_mappings.keys())
        for provider, mapping in self.provider_mappings.items():
            if provider not in allowed_providers:
                continue
            for model_name in mapping.model_name_enum:
                if self.using_remote_credential_pools:
                    raise NotImplementedError("Remote credential pools are not implemented yet")
                else:
                    pool = mapping.local_credential_pool_cls(
                        model_provider=provider,
                        target_model=model_name,
                        account_credentials=mapping.account_credentials,
                    )
                    if isinstance(pool, CredentialPoolBase):
                        await pool.start()
                    else:
                        log.warning(f"Pool {pool} is not a CredentialPoolBase")
                self._credential_pools[provider][model_name.value] = pool

    def stop_all_pools(self):
        """Stop all credential pools."""
        for provider, pools in self._credential_pools.items():
            for pool in pools.values():
                if isinstance(pool, CredentialPoolBase):
                    pool.stop()


if __name__ == "__main__":
    import asyncio

    async def test_model_switcher():
        """Test the ModelSwitcher functionality."""

        switcher = AgentSwitcher(providers=['laozhang', 'laozhang_sgp'])
        await switcher.start_all_pools()
        credential_pool = switcher.get_credential_pool('laozhang_sgp', 'gpt-4o')
        print(f"成功获取凭证池：{credential_pool.get_model_credentials()}")

        switcher.stop_all_pools()

    try:
        asyncio.run(test_model_switcher())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
