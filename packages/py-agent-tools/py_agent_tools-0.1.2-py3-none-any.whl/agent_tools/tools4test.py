import functools
from typing import Any, Callable, Coroutine

from pydantic_ai.settings import ModelSettings

from agent_tools._log import log
from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolProtocol, LocalCredentialPool
from agent_tools.provider_config import AccountCredential


def with_agent_switcher(providers: list[str]):
    """
    装饰器：自动管理 AgentSwitcher 的生命周期。

    自动处理 start_all_pools() 和 stop_all_pools() 的调用，
    确保资源正确清理。

    Args:
        providers: 要启动的provider列表

    Example:
        @with_agent_switcher(providers=["ark"])
        async def test(agent_switcher):
            # 使用 agent_switcher 进行测试
            pass
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            from agent_tools.agent_switcher import AgentSwitcher

            # 创建并启动 agent_switcher
            agent_switcher = AgentSwitcher(providers=providers)
            try:
                await agent_switcher.start_all_pools()

                # 将 agent_switcher 传递给被装饰的函数
                return await func(agent_switcher, *args, **kwargs)

            finally:
                # 确保在函数结束时停止所有pools
                agent_switcher.stop_all_pools()

        return wrapper

    return decorator


async def test_credential_pool_manager(
    credential_pool_cls: type[CredentialPoolProtocol],
    agent_cls: type[AgentBase],
    model_provider: str,
    target_model: str,
    account_credentials: list[AccountCredential],
    model_settings: ModelSettings,
    stream: bool = False,
):
    credential_pool = credential_pool_cls(
        model_provider=model_provider,
        target_model=target_model,
        account_credentials=account_credentials,
    )
    if isinstance(credential_pool, LocalCredentialPool):
        await credential_pool.start()

    agent_tool = await agent_cls.create(
        credential_pool=credential_pool,
        model_settings=model_settings,
    )
    log.info("Agent created.")

    runner = await agent_tool.run("中国的首都是哪里？", stream=stream)
    print(runner.result)

    if isinstance(credential_pool, LocalCredentialPool):
        credential_pool.stop()


async def test_all_credentials(
    model_name_enum: type[ModelNameBase],
    model_settings: ModelSettings,
    credential_pool_cls: type[CredentialPoolProtocol],
    agent_cls: type[AgentBase],
    model_provider: str,
    account_credentials: list[AccountCredential],
):
    for model_name in model_name_enum:
        credential_pool = credential_pool_cls(
            model_provider=model_provider,
            target_model=model_name,
            account_credentials=account_credentials,
        )
        for credential in credential_pool.get_model_credentials():
            if "embedding" in model_name.value:
                continue
            try:
                agent = await agent_cls.create(
                    credential=credential,
                    model_settings=model_settings,
                )
                result = await agent.validate_credential()
                if result is True:
                    print(f"{credential.id} is valid.")
                else:
                    print(f"{credential.id} is invalid!")
            except Exception as e:
                print(f"error: {e}")
                raise
