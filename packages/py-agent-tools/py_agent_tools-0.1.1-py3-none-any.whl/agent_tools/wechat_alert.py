"""
微信企业群预警模块

提供异常处理和微信企业群消息推送功能。
"""

import asyncio
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type

import aiohttp
from pydantic import BaseModel, Field
from pydantic_ai.exceptions import AgentRunError, ModelHTTPError, UserError

from agent_tools._log import log


class WechatAlertConfig(BaseModel):
    """微信企业群预警配置"""

    webhook_url: str = Field(description="企业微信群机器人")
    enabled: bool = Field(default=True, description="是否启用微信预警")
    alert_levels: list[str] = Field(default=["ERROR", "CRITICAL"], description="需要预警的异常级别")
    max_message_length: int = Field(default=2000, description="消息最大长度，超长会被截断")
    retry_times: int = Field(default=3, description="发送失败重试次数")
    retry_delay: float = Field(default=1.0, description="重试间隔(秒)")


class ExceptionInfo(BaseModel):
    """异常信息模型"""

    exception_type: str = Field(description="异常类型")
    exception_message: str = Field(description="异常消息")
    traceback: str = Field(description="异常堆栈")
    agent_name: str = Field(description="Agent名称")
    model_name: Optional[str] = Field(default=None, description="模型名称")
    provider: Optional[str] = Field(default=None, description="提供商")
    timestamp: datetime = Field(default_factory=datetime.now, description="异常发生时间")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class WechatAlertManager:
    """微信预警管理器"""

    def __init__(self, config: WechatAlertConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _send_message(self, message: str) -> bool:
        """发送微信消息"""
        if not self.config.enabled:
            log.info("微信预警已禁用，跳过消息发送")
            return True

        if not self.config.webhook_url:
            log.warning("微信webhook URL未配置，跳过消息发送")
            return False

        # 截断过长的消息
        if len(message) > self.config.max_message_length:
            message = message[: self.config.max_message_length - 3] + "..."

        payload = {"msgtype": "text", "text": {"content": message}}

        session = await self._get_session()

        for attempt in range(self.config.retry_times):
            try:
                async with session.post(
                    self.config.webhook_url, json=payload, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("errcode") == 0:
                            log.info("微信预警消息发送成功")
                            return True
                        else:
                            log.error(f"微信API返回错误: {result}")
                    else:
                        log.error(f"微信API请求失败，状态码: {response.status}")

            except Exception as e:
                log.error(f"发送微信消息失败 (尝试 {attempt + 1}/{self.config.retry_times}): {e}")

            if attempt < self.config.retry_times - 1:
                await asyncio.sleep(self.config.retry_delay)

        return False

    def format_exception_message(self, exception_info: ExceptionInfo) -> str:
        """格式化异常消息"""
        # 标题
        message_parts = [
            "🚨 **Agent异常预警**",
            "",
        ]

        # 基础信息
        message_parts.extend(
            [
                "📋 基础信息",
                f"• Agent: {exception_info.agent_name}",
                f"• 时间: {exception_info.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            ]
        )

        # 模型信息
        if exception_info.provider and exception_info.model_name:
            message_parts.append(f"• 模型: {exception_info.provider}/{exception_info.model_name}")
        elif exception_info.model_name:
            message_parts.append(f"• 模型: {exception_info.model_name}")

        # 异常
        message_parts.extend(
            [
                "",
                "❌ 异常详情",
                f"• 类型: {exception_info.exception_type}",
                f"• 消息: {exception_info.exception_message[:80]}{'...' if len(exception_info.exception_message) > 80 else ''}",  # noqa
            ]
        )

        # 堆栈信息
        stack_info = self._extract_key_stack_info(exception_info.traceback)
        if stack_info:
            message_parts.extend(["", "🔍 关键堆栈", f"```\n{stack_info}\n```"])

        # 上下文信息
        if exception_info.context:
            context_summary = self._summarize_context(exception_info.context)
            if context_summary:
                message_parts.extend(["", "⚙️ 执行上下文", context_summary])

        return "\n".join(message_parts)

    def _extract_key_stack_info(self, traceback: str) -> str:
        """提取关键堆栈信息"""
        lines = traceback.split('\n')
        key_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 保留异常类型行
            if line.startswith(('Traceback', 'File', '  File')):
                key_lines.append(line)
            # 保留包含 agent_tools 的行
            elif 'agent_tools' in line:
                key_lines.append(line)
            # 保留异常信息行
            elif any(keyword in line for keyword in ['Error:', 'Exception:', 'Failed:', 'Invalid']):
                key_lines.append(line)
            # 保留最后几行
            elif len(key_lines) < 5:
                key_lines.append(line)

        #
        if len(key_lines) > 8:
            return '\n'.join(key_lines[:4] + ['...'] + key_lines[-3:])

        return '\n'.join(key_lines)

    def _summarize_context(self, context: dict) -> str:
        """简化上下文信息"""
        summary_parts = []

        if 'function' in context:
            summary_parts.append(f"• 函数: {context['function']}")

        if 'agent_attributes' in context:
            attrs = context['agent_attributes']
            if attrs.get('timeout'):
                summary_parts.append(f"• 超时: {attrs['timeout']}s")
            if attrs.get('max_retries'):
                summary_parts.append(f"• 重试: {attrs['max_retries']}")

        if summary_parts:
            return '\n'.join(summary_parts)

        return ""

    async def send_exception_alert(self, exception_info: ExceptionInfo) -> bool:
        """发送异常预警"""
        try:
            message = self.format_exception_message(exception_info)
            return await self._send_message(message)
        except Exception as e:
            log.error(f"格式化或发送异常预警失败: {e}")
            return False

    async def close(self):
        """关闭HTTP会话"""
        if self._session and not self._session.closed:
            await self._session.close()


# 全局预警管理器实例
_alert_manager: Optional[WechatAlertManager] = None


def get_alert_manager() -> WechatAlertManager:
    """获取全局预警管理器实例"""
    global _alert_manager
    if _alert_manager is None:
        # 从配置中读取设置
        from agent_tools.settings import agent_settings

        config = WechatAlertConfig(
            webhook_url=agent_settings.wechat_alert.webhook_url,
            enabled=agent_settings.wechat_alert.enabled,
            alert_levels=agent_settings.wechat_alert.alert_levels,
            max_message_length=agent_settings.wechat_alert.max_message_length,
            retry_times=agent_settings.wechat_alert.retry_times,
            retry_delay=agent_settings.wechat_alert.retry_delay,
        )
        _alert_manager = WechatAlertManager(config)
    return _alert_manager


def set_alert_manager(manager: WechatAlertManager):
    """设置全局预警管理器实例"""
    global _alert_manager
    _alert_manager = manager


def agent_exception_handler(  # noqa: C901
    alert_on_exceptions: Optional[list[Type[Exception]]] = None,
    include_context: bool = True,  # noqa
):
    """
    Agent异常处理装饰器

    Args:
        alert_on_exceptions: 需要预警的异常类型列表，None表示所有异常
        include_context: 是否包含上下文信息
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取agent实例信息
            agent_instance = args[0] if args else None
            agent_name = agent_instance.__class__.__name__ if agent_instance else "Unknown"

            # 获取模型和提供商信息
            model_name = None
            provider = None
            if (
                agent_instance
                and hasattr(agent_instance, 'credential')
                and agent_instance.credential
            ):
                model_name = agent_instance.credential.model_name
                provider = (
                    agent_instance.credential.model_provider
                    if hasattr(agent_instance.credential, 'model_provider')
                    else None
                )

            try:
                return await func(*args, **kwargs)
            except (ModelHTTPError, AgentRunError, UserError) as e:
                # pydantic_ai的异常，直接发送预警
                log.info(f"装饰器捕获到 pydantic_ai 异常: {type(e).__name__}: {e}")

                context = {}
                if include_context:
                    context = {
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                        "agent_attributes": (
                            {
                                "timeout": getattr(agent_instance, 'timeout', None),
                                "max_retries": getattr(agent_instance, 'max_retries', None),
                                "system_prompt": getattr(agent_instance, 'system_prompt', None),
                            }
                            if agent_instance
                            else {}
                        ),
                    }

                exception_info = ExceptionInfo(
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                    traceback=traceback.format_exc(),
                    agent_name=agent_name,
                    model_name=model_name,
                    provider=provider,
                    context=context,
                )

                # 发送预警
                try:
                    alert_manager = get_alert_manager()
                    log.info("开始发送微信预警...")
                    await alert_manager.send_exception_alert(exception_info)
                    log.info("微信预警发送完成")
                except Exception as alert_error:
                    log.error(f"发送异常预警失败: {alert_error}")

                # 重新抛出异常
                raise
            except Exception as e:
                # 检查是否需要预警其他异常
                should_alert = alert_on_exceptions is None or any(
                    isinstance(e, exc_type) for exc_type in alert_on_exceptions
                )

                if should_alert:
                    # 构建异常信息
                    context = {}
                    if include_context:
                        context = {
                            "function": func.__name__,
                            "args_count": len(args),
                            "kwargs_keys": list(kwargs.keys()),
                            "agent_attributes": (
                                {
                                    "timeout": getattr(agent_instance, 'timeout', None),
                                    "max_retries": getattr(agent_instance, 'max_retries', None),
                                    "system_prompt": getattr(agent_instance, 'system_prompt', None),
                                }
                                if agent_instance
                                else {}
                            ),
                        }

                    exception_info = ExceptionInfo(
                        exception_type=type(e).__name__,
                        exception_message=str(e),
                        traceback=traceback.format_exc(),
                        agent_name=agent_name,
                        model_name=model_name,
                        provider=provider,
                        context=context,
                    )

                    # 发送预警
                    try:
                        alert_manager = get_alert_manager()
                        await alert_manager.send_exception_alert(exception_info)
                    except Exception as alert_error:
                        log.error(f"发送异常预警失败: {alert_error}")
                raise

        return wrapper

    return decorator


def setup_wechat_alert(
    webhook_url: str,
    enabled: bool = True,
    alert_levels: Optional[list[str]] = None,
    max_message_length: int = 2000,
    retry_times: int = 3,
    retry_delay: float = 1.0,
):
    """
    设置微信预警配置

    Args:
        webhook_url: 企业微信群机器人webhookURL
        enabled: 是否启用微信预警
        alert_levels: 需要预警的异常级别
        max_message_length: 消息最大长度
        retry_times: 发送失败重试次数
        retry_delay: 重试间隔(秒)
    """
    config = WechatAlertConfig(
        webhook_url=webhook_url,
        enabled=enabled,
        alert_levels=alert_levels or ["ERROR", "CRITICAL"],
        max_message_length=max_message_length,
        retry_times=retry_times,
        retry_delay=retry_delay,
    )

    manager = WechatAlertManager(config)
    set_alert_manager(manager)

    log.info(f"微信预警配置已设置: enabled={enabled}, " f"webhook_url={webhook_url[:20]}...")


async def close_wechat_alert():
    """关闭微信预警管理器"""
    global _alert_manager
    if _alert_manager:
        await _alert_manager.close()
        _alert_manager = None
