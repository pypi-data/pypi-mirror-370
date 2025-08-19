from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.provider_config import AccountCredential


class LaozhangModelName(ModelNameBase):

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O4_MINI = "o4-mini"
    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"

    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"

    GROK_4 = "grok-4"
    GROK_4_0709 = "grok-4-0709"

    CLAUDE_SONNET_4_20250514 = "claude-sonnet-4-20250514"
    CLAUDE_SONNET_4_20250514_THINKING = "claude-sonnet-4-20250514-thinking"


class LaozhangEmbeddingModelName(ModelNameBase):
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"


class LaozhangAgent(AgentBase):
    def create_client(self):
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        return AsyncOpenAI(
            api_key=self.credential.api_key,
            base_url=self.credential.base_url,
        )

    def create_model(self):
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        client = self.create_client()
        return OpenAIModel(
            model_name=self.credential.model_name,
            provider=OpenAIProvider(openai_client=client),
        )


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await LaozhangAgent.create(credential=credential)
    return await agent.validate_credential()


class LaozhangCredentialPool(CredentialPoolBase):
    def __init__(
        self,
        model_provider: str,
        target_model: LaozhangModelName,
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
        temperature=1.0,
        max_tokens=8192,
    )
    provider = "laozhang"

    @with_agent_switcher(providers=[provider])
    async def test(agent_switcher):
        """Main function that runs all tests with proper cleanup."""
        await test_credential_pool_manager(
            credential_pool_cls=LaozhangCredentialPool,
            agent_cls=LaozhangAgent,
            model_provider=provider,
            account_credentials=agent_switcher.provider_mappings[provider].account_credentials,
            # target_model=LaozhangModelName.GROK_4,  # which is forbiden in credential file
            target_model=LaozhangModelName.GPT_4O,
            model_settings=model_settings,
            stream=True,
        )
        await test_all_credentials(
            model_name_enum=LaozhangModelName,
            model_settings=model_settings,
            credential_pool_cls=LaozhangCredentialPool,
            agent_cls=LaozhangAgent,
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
