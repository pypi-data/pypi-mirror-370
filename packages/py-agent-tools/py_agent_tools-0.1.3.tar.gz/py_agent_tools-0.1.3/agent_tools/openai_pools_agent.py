from openai import AsyncOpenAI
from pydantic_ai.exceptions import AgentRunError, ModelHTTPError, UserError
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.provider_config import AccountCredential
from agent_tools.wechat_alert import agent_exception_handler


class OpenAIPoolsModelName(ModelNameBase):
    GPT_4O = "gpt-4o"


class OpenAIPoolsAgent(AgentBase):
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
        raise NotImplementedError("OpenAIPoolsAgent does not support embedding")

    @agent_exception_handler()
    async def validate_credential(self) -> bool:
        "重写"
        agent = self.create_agent()
        try:
            await self.runner.run(agent, 'this is a test, just echo "hello"', stream=False)
            return True
        except (ModelHTTPError, AgentRunError, UserError):
            raise
        except Exception:
            return False


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await OpenAIPoolsAgent.create(credential=credential)
    return await agent.validate_credential()


class OpenAIPoolsCredentialPool(CredentialPoolBase):
    def __init__(
        self,
        model_provider: str,
        target_model: OpenAIPoolsModelName,
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

    @with_agent_switcher(providers=["openai_pools"])
    async def test(agent_switcher):
        """Main function that runs all tests with proper cleanup."""
        await test_credential_pool_manager(
            credential_pool_cls=OpenAIPoolsCredentialPool,
            agent_cls=OpenAIPoolsAgent,
            model_provider="openai_pools",
            account_credentials=agent_switcher.provider_mappings[
                "openai_pools"
            ].account_credentials,
            target_model=OpenAIPoolsModelName.GPT_4O,
            model_settings=model_settings,
            stream=False,
        )
        await test_all_credentials(
            model_name_enum=OpenAIPoolsModelName,
            model_settings=model_settings,
            credential_pool_cls=OpenAIPoolsCredentialPool,
            agent_cls=OpenAIPoolsAgent,
            model_provider="openai_pools",
            account_credentials=agent_switcher.provider_mappings[
                "openai_pools"
            ].account_credentials,
        )

    try:
        asyncio.run(test())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
