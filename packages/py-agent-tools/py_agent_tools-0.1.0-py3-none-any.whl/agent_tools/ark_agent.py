from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.provider_config import AccountCredential


class ArkModelName(ModelNameBase):
    DEEPSEEK_R1_250528 = "deepseek-r1-250528"
    DEEPSEEK_V3_250324 = "deepseek-v3-250324"
    DOUBAO_SEED_1_6_250615 = "doubao-seed-1-6-250615"
    DOUBAO_SEED_1_6_THINKING_250615 = "doubao-seed-1-6-thinking-250615"
    DOUBAO_SEED_1_6_FLASH_250615 = "doubao-seed-1-6-flash-250615"


class ArkEmbeddingModelName(ModelNameBase):
    DOUBAO_EMBEDDING_VISION_250328 = "doubao-embedding-vision-250328"
    DOUBAO_EMBEDDING_LARGE_TEXT_240915 = "doubao-embedding-large-text-240915"


class ArkAgent(AgentBase):
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


async def validate_fn(credential: ModelCredential) -> bool:
    agent_tool = await ArkAgent.create(credential=credential)
    return await agent_tool.validate_credential()


class ArkCredentialPool(CredentialPoolBase):
    def __init__(
        self,
        model_provider: str,
        target_model: ArkModelName,
        account_credentials: list[AccountCredential],
    ):
        super().__init__(
            model_provider=model_provider,
            account_credentials=account_credentials,
            target_model=target_model,
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
    provider = "ark"

    @with_agent_switcher(providers=[provider])
    async def test(agent_switcher):
        """Main function that runs all tests with proper cleanup."""
        await test_credential_pool_manager(
            credential_pool_cls=ArkCredentialPool,
            agent_cls=ArkAgent,
            model_provider=provider,
            account_credentials=agent_switcher.provider_mappings[provider].account_credentials,
            target_model=ArkModelName.DOUBAO_SEED_1_6_250615,
            model_settings=model_settings,
        )
        await test_all_credentials(
            model_name_enum=ArkModelName,
            model_settings=model_settings,
            credential_pool_cls=ArkCredentialPool,
            agent_cls=ArkAgent,
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
