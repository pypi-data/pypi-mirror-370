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
        timeout: Request timeout in seconds (default: 120.0 for better handling of 504 errors).
        base_retry_delay: Base delay for exponential backoff (default: 2.0 seconds).
    """

    def __init__(
        self,
        credential: ModelCredential | None = None,
        credential_pool: CredentialPoolProtocol | None = None,
        system_prompt: str | None = None,
        timeout: float = 120.0,  # 增加默认超时时间到120秒
        max_retries: int = 3,
        model_settings: ModelSettings = ModelSettings(),
        base_retry_delay: float = 1.0
    ):
        if (credential is None) == (credential_pool is None):
            raise ValueError("Exactly one of credential or credential_pool must be None")

        self.credential = credential
        self.credential_pool = credential_pool
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay  # 新增：指数退避基础延迟
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
        timeout: float = 120.0,  # 增加默认超时时间到120秒
        max_retries: int = 3,
        model_settings: ModelSettings = ModelSettings(temperature=1),
        base_retry_delay: float = 1.0,  # 新增：指数退避基础延迟
    ) -> "AgentBase":
        instance = cls(
            credential,
            credential_pool,
            system_prompt,
            timeout,
            max_retries,
            model_settings,
            base_retry_delay,
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
            # 使用指数退避策略
            delay = self.base_retry_delay * (2 ** (3 - self.max_retries))  # 2, 4, 8秒
            log.info(f"等待 {delay} 秒后重试...")
            await asyncio.sleep(delay)
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
        """Run with retries and optimized timeout handling"""
        agent = self.create_agent()
        try:
            # 为长时间运行的请求设置更长的超时
            request_timeout = kwargs.get('timeout', self.timeout)
            if request_timeout < 60:  # 如果超时时间小于60秒，自动调整
                request_timeout = max(60, self.timeout)
                log.info(f"调整超时时间到 {request_timeout} 秒以处理可能的504错误")

            await self.runner.run(
                agent,
                prompt,
                images=images,
                postprocess_fn=postprocess_fn,
                stream=stream,
                timeout=request_timeout,
                **kwargs,
            )
        except (ModelHTTPError, AgentRunError, UserError) as e:
            # 检查是否是504错误，如果是则记录特殊处理
            if isinstance(e, ModelHTTPError) and hasattr(e, 'status_code') and e.status_code == 504:
                log.warning(f"检测到504 Gateway Timeout错误，将进行重试: {e}")
                self._last_exception = e
                await self._switch_credential()
                return await self.run(
                    prompt, images=images, postprocess_fn=postprocess_fn, stream=stream, **kwargs
                )
            # 其他 pydantic_ai 异常，直接重新抛出，让装饰器处理
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
