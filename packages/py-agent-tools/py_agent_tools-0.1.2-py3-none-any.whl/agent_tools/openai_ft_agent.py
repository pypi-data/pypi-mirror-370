from agent_tools.agent_base import ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase
from agent_tools.openai_agent import OpenAIAgent, validate_fn
from agent_tools.provider_config import AccountCredential


class OpenAIFineTuningModelName(ModelNameBase):
    FT_O4_MINI_ELEMENTS_20250730 = "ft-o4-mini-elements-20250730"


class OpenAIFineTuningCredentialPool(CredentialPoolBase):
    def __init__(
        self,
        model_provider: str,
        target_model: OpenAIFineTuningModelName,
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
        temperature=0.7,
        max_tokens=8192,
    )
    provider = "openai_ft"

    @with_agent_switcher(providers=[provider])
    async def test(agent_switcher):
        """Main function that runs all tests with proper cleanup."""
        await test_credential_pool_manager(
            credential_pool_cls=OpenAIFineTuningCredentialPool,
            agent_cls=OpenAIAgent,
            model_provider=provider,
            account_credentials=agent_switcher.provider_mappings[provider].account_credentials,
            target_model=OpenAIFineTuningModelName.FT_O4_MINI_ELEMENTS_20250730,
            model_settings=model_settings,
        )
        await test_all_credentials(
            model_name_enum=OpenAIFineTuningModelName,
            model_settings=model_settings,
            credential_pool_cls=OpenAIFineTuningCredentialPool,
            agent_cls=OpenAIAgent,
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
