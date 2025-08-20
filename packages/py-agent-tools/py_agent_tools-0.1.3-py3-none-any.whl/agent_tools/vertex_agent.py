"""
Not tested yet.
"""

import httpx
from google.oauth2 import service_account
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.provider_config import AccountCredential


class VertexModelName(ModelNameBase):
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_2_5_PRO = "gemini-2.5-pro"


class VertexAgent(AgentBase):
    def create_client(self) -> httpx.AsyncClient:
        raise NotImplementedError("VertexAgent does not support create_client")

    def create_model(self) -> GoogleModel:
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        credentials = service_account.Credentials.from_service_account_info(
            self.credential.account_info,
            scopes=['https://www.googleapis.com/auth/cloud-platform'],
        )
        return GoogleModel(
            model_name=self.credential.model_name,
            provider=GoogleProvider(credentials=credentials),
        )

    def embedding(self, input: str, dimensions: int = 1024):
        raise NotImplementedError("VertexAgent does not support embedding")


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await VertexAgent.create(credential=credential)
    return await agent.validate_credential()


class VertexCredentialPool(CredentialPoolBase):
    def __init__(
        self,
        model_provider: str,
        target_model: VertexModelName,
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
    provider = "vertex"

    @with_agent_switcher(providers=[provider])
    async def test(agent_switcher):
        """Main function that runs all tests with proper cleanup."""
        await test_credential_pool_manager(
            credential_pool_cls=VertexCredentialPool,
            agent_cls=VertexAgent,
            model_provider=provider,
            account_credentials=agent_switcher.provider_mappings[provider].account_credentials,
            target_model=VertexModelName.GEMINI_2_0_FLASH,
            model_settings=model_settings,
        )
        await test_all_credentials(
            model_name_enum=VertexModelName,
            model_settings=model_settings,
            credential_pool_cls=VertexCredentialPool,
            agent_cls=VertexAgent,
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
