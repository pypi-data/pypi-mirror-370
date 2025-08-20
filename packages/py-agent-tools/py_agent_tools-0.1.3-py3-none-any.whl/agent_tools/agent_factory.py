from typing import Any, Type

from pydantic_ai import Agent, EndStrategy
from pydantic_ai.models.openai import Model


class AgentFactory:
    """Factory class for creating different types of agents."""

    DEFAULT_SYSTEM_PROMPT = 'system'
    DEFAULT_RETRIES = 1
    DEFAULT_DEPS_TYPE = str
    DEFAULT_END_STRATEGY: EndStrategy = 'early'

    @staticmethod
    def create_agent(
        model: Model,
        system_prompt: str | None = None,
        deps_type: Type[Any] | None = None,
        retries: int | None = None,
    ) -> Agent[Any, str]:
        return Agent(
            model,
            retries=retries or AgentFactory.DEFAULT_RETRIES,
            deps_type=deps_type or AgentFactory.DEFAULT_DEPS_TYPE,
            system_prompt=system_prompt or AgentFactory.DEFAULT_SYSTEM_PROMPT,
            end_strategy=AgentFactory.DEFAULT_END_STRATEGY,
        )
