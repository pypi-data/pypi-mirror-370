import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable

from pydantic_ai import Agent, BinaryContent
from pydantic_ai.exceptions import AgentRunError, ModelHTTPError, UserError
from pydantic_ai.models.openai import Model
from pydantic_ai.settings import ModelSettings

from agent_tools._log import log
from agent_tools.agent_factory import AgentFactory
from agent_tools.agent_runner import AgentRunner
from agent_tools.credential_pool_base import CredentialPoolProtocol, ModelCredential, StatusType
from agent_tools.wechat_alert import agent_exception_handler


class ModelNameBase(str, Enum):
    """
    表示已测试的模型名称。
    """

    pass


class AgentBase(ABC):
    """Base class for all agents.

    Args:
        credential or credential_pool: Exactly one of credential or credential_pool
            must be provided.
        system_prompt: The system prompt to use for the agent.
        max_retries: The maximum number of retries to make when the agent fails.
        model_settings: The model settings to use for the agent.
    """

    def __init__(
        self,
        credential: ModelCredential | None = None,
        credential_pool: CredentialPoolProtocol | None = None,
        system_prompt: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
        model_settings: ModelSettings = ModelSettings(),
    ):
        if (credential is None) == (credential_pool is None):
            raise ValueError("Exactly one of credential or credential_pool must be None")

        self.credential = credential
        self.credential_pool = credential_pool
        self.timeout = timeout
        self.max_retries = max_retries
        self.system_prompt: str | None = system_prompt
        self.runner = AgentRunner(
            model_settings=model_settings,
        )

    @classmethod
    async def create(
        cls,
        credential: ModelCredential | None = None,
        credential_pool: CredentialPoolProtocol | None = None,
        system_prompt: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
        model_settings: ModelSettings = ModelSettings(temperature=1),
    ) -> "AgentBase":
        instance = cls(
            credential,
            credential_pool,
            system_prompt,
            timeout,
            max_retries,
            model_settings,
        )
        await instance._initialize_credential(credential, credential_pool)
        return instance

    def _update_model_settings(self):
        if self.credential is None:
            raise ValueError("Credential is not initialized!")
        if len(self.credential.model_settings.keys()) > 0:
            for k, v in self.credential.model_settings.items():
                if v is None and self.runner.model_settings.get(k) is not None:
                    log.warning(f"Delete '{k}' from model settings")
                    self.runner.model_settings.pop(k, None)  # type: ignore
                else:
                    if v != self.runner.model_settings.get(k):
                        log.info(f"Update '{k}' from {self.runner.model_settings.get(k)} to {v}")
                        self.runner.model_settings[k] = v  # type: ignore
            log.info(f"Model settings in agent: {self.runner.model_settings}")

    async def _initialize_credential(
        self,
        credential: ModelCredential | None,
        credential_pool: CredentialPoolProtocol | None,
    ):
        if credential_pool is not None:
            if len(credential_pool.get_model_credentials()) == 0:
                raise ValueError("Credential pool is empty")
            elif len(credential_pool.get_model_credentials()) == 1:
                self.credential = credential_pool.get_model_credentials()[0]
                self.credential_pool = None
            else:
                self.credential_pool = credential_pool
                self.credential = await credential_pool.get_best()
        elif credential is not None:
            self.credential = credential
            self.credential_pool = None
        else:
            raise ValueError("Either credential or credential_pool must be provided")
        self._update_model_settings()

    async def _switch_credential(self):
        if self.credential_pool is not None and self.credential is not None:
            await self.credential_pool.update_status(self.credential, StatusType.ERROR)
            self.credential = await self.credential_pool.get_best()
        else:
            await asyncio.sleep(3)
        self.max_retries -= 1
        if self.max_retries <= 0:
            # 重新抛出最后一个异常，让装饰器能够捕获
            if hasattr(self, '_last_exception'):
                raise self._last_exception
            else:
                raise ValueError("Max retries reached")
        self._update_model_settings()

    @abstractmethod
    def create_client(self) -> Any:
        """Create a client for the agent by self.credential"""
        pass

    @abstractmethod
    def create_model(self) -> Model:
        """Create a model for the agent according to model provider"""
        pass

    def create_agent(self) -> Agent[Any, str]:
        """Default agent creation function"""
        model = self.create_model()
        return AgentFactory.create_agent(
            model,
            system_prompt=self.system_prompt,
        )

    @agent_exception_handler()
    async def validate_credential(self) -> bool:
        agent = self.create_agent()
        try:
            await self.runner.run(agent, 'this is a test, just echo "hello"', stream=True)
            return True
        except (ModelHTTPError, AgentRunError, UserError):
            raise
        except Exception:
            return False

    @agent_exception_handler()
    async def run(
        self,
        prompt: str,
        images: list[BinaryContent] = [],
        postprocess_fn: Callable[[str], Any] | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> AgentRunner:
        """Run with retries"""
        agent = self.create_agent()
        try:
            await self.runner.run(
                agent, prompt, images=images, postprocess_fn=postprocess_fn, stream=stream, **kwargs
            )
        except (ModelHTTPError, AgentRunError, UserError):
            # pydantic_ai的异常，直接重新抛出，让装饰器处理
            raise
        except Exception as e:
            # 保存最后一个异常
            self._last_exception = e
            await self._switch_credential()
            return await self.run(
                prompt, images=images, postprocess_fn=postprocess_fn, stream=stream, **kwargs
            )
        return self.runner

    @agent_exception_handler()
    async def embedding(
        self,
        input: str,
        dimensions: int = 1024,
    ) -> AgentRunner | None:
        """Embedding with retries"""
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        if 'embedding' not in self.credential.model_name:
            raise ValueError("Model is not an embedding model, use run instead")
        try:
            await self.runner.embedding(
                self.create_client(),
                self.credential.model_name,
                input,
                dimensions,
            )
        except (ModelHTTPError, AgentRunError, UserError):
            raise
        except Exception as e:
            # 保存最后一个异常
            self._last_exception = e
            await self._switch_credential()
            return await self.embedding(input, dimensions)
        return self.runner
