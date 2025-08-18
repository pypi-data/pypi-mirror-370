from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.provider_config import AccountCredential


class BailianModelName(ModelNameBase):
    QWEN_TURBO = "qwen-turbo"
    QWEN_PLUS = "qwen-plus"


class BailianAgent(AgentBase):
    """Bailian agent.

    Args:
        model_settings: The model settings to use for the agent.
        可配置参数：
        https://bailian.console.aliyun.com/?spm=5176.29597918.J_SEsSjsNv72yRuRFS2VknO.2.2eac7b08zY6yxZ&tab=api#/api/?type=model&url=https%3A%2F%2Fhelp.aliyun.com%2Fdocument_detail%2F2712576.html
        限制思考长度：
        https://help.aliyun.com/zh/model-studio/deep-thinking?spm=0.0.0.i0#e7c0002fe4meu
    """

    def create_client(self) -> AsyncOpenAI:
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        return AsyncOpenAI(
            api_key=self.credential.api_key,
            base_url=self.credential.base_url,
            timeout=self.timeout,
        )

    def create_model(self) -> OpenAIModel:
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        client = self.create_client()
        return OpenAIModel(
            model_name=self.credential.model_name,
            provider=OpenAIProvider(openai_client=client),
        )

    def embedding(self, input: str, dimensions: int = 1024):
        raise NotImplementedError("BailianAgent does not support embedding")


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await BailianAgent.create(credential=credential)
    return await agent.validate_credential()


class BailianCredentialPool(CredentialPoolBase):
    def __init__(
        self,
        model_provider: str,
        target_model: BailianModelName,
        account_credentials: list[AccountCredential],
    ):
        super().__init__(
            model_provider=model_provider,
            target_model=target_model,
            account_credentials=account_credentials,
            validate_fn=validate_fn,
        )


if __name__ == "__main__":
    import asyncio

    from pydantic_ai.settings import ModelSettings

    from agent_tools.tools4test import (
        test_all_credentials,
        test_credential_pool_manager,
        with_agent_switcher,
    )

    model_settings = ModelSettings(
        temperature=0.0,
        max_tokens=8192,
    )
    provider = "bailian"

    @with_agent_switcher(providers=[provider])
    async def test(agent_switcher):
        """Main function that runs all tests with proper cleanup."""
        await test_credential_pool_manager(
            credential_pool_cls=BailianCredentialPool,
            agent_cls=BailianAgent,
            model_provider=provider,
            account_credentials=agent_switcher.provider_mappings[provider].account_credentials,
            target_model=BailianModelName.QWEN_PLUS,
            model_settings=model_settings,
        )
        await test_all_credentials(
            model_name_enum=BailianModelName,
            model_settings=model_settings,
            credential_pool_cls=BailianCredentialPool,
            agent_cls=BailianAgent,
            model_provider=provider,
            account_credentials=agent_switcher.provider_mappings[provider].account_credentials,
        )

    try:
        asyncio.run(test())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
