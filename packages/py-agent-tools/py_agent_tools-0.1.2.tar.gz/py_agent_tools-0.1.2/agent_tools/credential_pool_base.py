import asyncio
from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Protocol, Union, runtime_checkable

from pydantic import BaseModel

from agent_tools._log import log
from agent_tools.provider_config import AccountCredential
from agent_tools.settings import agent_settings


class StatusType(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class ModelCredential(BaseModel):
    id: str
    base_url: str = ""
    api_key: str = ""
    account_info: dict = {}
    api_version: str = ""
    model_provider: str = ""
    model_name: str = ""
    deployment: str = ""
    model_settings: dict = {}


class ModelCredentialWithStatus(BaseModel):
    id: str
    credential: ModelCredential
    status: StatusType
    last_checked: datetime


class ModelCredentialStatistics(BaseModel):
    model_name: str
    active: int = 0
    inactive: int = 0
    error: int = 0
    rate_limited: int = 0


def make_id(
    model_provider: str,
    account_id: str,
    group_id: str,
    model_name: str,
    deployment: str,
) -> str:
    id = ''
    if model_provider:
        id += f'{model_provider}'
    if account_id:
        id += f'_{account_id}'
    if group_id:
        id += f'_{group_id}'
    if model_name:
        id += f'_{model_name}'
    if deployment:
        id += f'_{deployment}'
    if not id:
        raise ValueError('id is empty')
    return id


@runtime_checkable
class CredentialPoolProtocol(Protocol):
    def __init__(self, target_model: str, **kwargs) -> None: ...

    def get_model_credentials(self) -> list[ModelCredential]: ...

    async def get_best(self) -> ModelCredential: ...

    async def update_status(self, credential: ModelCredential, status: StatusType) -> None: ...


class RemoteCredentialPool(CredentialPoolProtocol):
    def __init__(self, target_model: str):
        self.target_model = target_model
        self.model_credentials: list[ModelCredential] = self.get_model_credentials()

    def get_model_credentials(self) -> list[ModelCredential]:
        raise NotImplementedError

    async def get_best(self) -> ModelCredential:
        raise NotImplementedError

    async def update_status(self, credential: ModelCredential, status: StatusType) -> None:
        raise NotImplementedError


class LocalCredentialPool(CredentialPoolProtocol):
    def __init__(
        self, model_provider: str, target_model: str, account_credentials: list[AccountCredential]
    ):
        self.model_provider = model_provider
        self.target_model = target_model
        self.account_credentials = account_credentials
        self.model_credentials: list[ModelCredential] = self.get_model_credentials()

    def get_model_credentials(self) -> list[ModelCredential]:
        raise NotImplementedError

    async def get_best(self) -> ModelCredential:
        raise NotImplementedError

    async def update_status(self, credential: ModelCredential, status: StatusType) -> None:
        raise NotImplementedError

    async def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError


class CredentialPoolBase(ABC, LocalCredentialPool):
    """
    Credential pool is a pool of credentials for a specific model.
    It is used to:
        - select the best credential for a specific model.
        - update the status of the credential.
    """

    def __init__(
        self,
        model_provider: str,
        account_credentials: list[AccountCredential],
        target_model: str,
        validate_fn: Callable[[ModelCredential], Union[bool, Coroutine[Any, Any, bool]]],
        health_check_interval: int = agent_settings.default_model_health_check_interval,
    ):
        super().__init__(model_provider, target_model, account_credentials)
        self._running = False
        self._lock = asyncio.Lock()
        self._health_check_task: asyncio.Task | None = None
        self.credential_pool: dict[str, ModelCredentialWithStatus] = {}
        self.validate_fn = validate_fn
        self.health_check_interval = health_check_interval

    @property
    def supported_models(self) -> list[str]:
        supported_models: set[str] = set()
        for account_credential in self.account_credentials:
            for model in account_credential.supported_models:
                supported_models.add(model.model_name)
        return list(supported_models)

    def get_model_credentials(self) -> list[ModelCredential]:
        if self.target_model not in self.supported_models:
            return []
        model_credentials: list[ModelCredential] = []
        for account_credential in self.account_credentials:
            for model in account_credential.supported_models:
                if model.model_name != self.target_model:
                    continue
                model_credentials.append(
                    ModelCredential(
                        id=make_id(
                            model_provider=self.model_provider,
                            account_id=account_credential.account_id,
                            group_id=account_credential.group_id,
                            model_name=model.model_name,
                            deployment=model.deployment,
                        ),
                        base_url=account_credential.base_url,
                        api_key=account_credential.api_key,
                        account_info=account_credential.account_info,
                        api_version=model.api_version,
                        model_provider=model.model_provider,
                        model_name=(
                            model.ckpt_id
                            if self.model_provider.endswith('_ft')
                            else model.model_name
                        ),
                        deployment=model.deployment,
                        model_settings=model.model_settings,
                    )
                )
        if len(model_credentials) == 0:
            raise ValueError(f'No model credentials found for {self.target_model}')
        return model_credentials

    async def get_best(self) -> ModelCredential:
        active_credentials = [
            credential.credential
            for credential in self.credential_pool.values()
            if credential.status == StatusType.ACTIVE
        ]

        log.info(f'Credential pool status for {self.target_model}:')
        log.info(f'Total credentials in pool: {len(self.credential_pool)}')
        log.info(f'Active credentials: {len(active_credentials)}')
        for cred_id, cred_status in self.credential_pool.items():
            log.info(f'  {cred_id}: {cred_status.status}')

        if not active_credentials:
            # If no active credentials are available, reset all credentials to ACTIVE
            # This provides a fallback mechanism when all credentials have been marked as ERROR
            log.warning(
                f'No active credentials found for {self.target_model}, '
                f'resetting all credentials to ACTIVE'
            )
            async with self._lock:
                for credential in self.credential_pool.values():
                    credential.status = StatusType.ACTIVE
                    credential.last_checked = datetime.now()

            # Get the list again after resetting
            active_credentials = [
                credential.credential
                for credential in self.credential_pool.values()
                if credential.status == StatusType.ACTIVE
            ]

            log.info(f'After reset - Active credentials: {len(active_credentials)}')

            if not active_credentials:
                log.error(f'Credential pool is completely empty for {self.target_model}')
                log.error(f'Model credentials count: {len(self.model_credentials)}')
                for cred in self.model_credentials:
                    log.error(f'  Model credential: {cred.id} - {cred.model_name}')
                raise ValueError(
                    f'No credentials available for {self.target_model} even after reset'
                )
        if len(active_credentials) == 0:
            raise ValueError(f'No credentials available for {self.target_model}')

        return min(
            active_credentials,
            key=lambda x: self.credential_pool[x.id].last_checked,
        )

    async def update_status(
        self,
        credential: ModelCredential,
        status: StatusType,
    ):
        async with self._lock:
            if credential.id in self.credential_pool.keys():
                self.credential_pool[credential.id].status = status
                self.credential_pool[credential.id].last_checked = datetime.now()
            else:
                self.credential_pool[credential.id] = ModelCredentialWithStatus(
                    id=credential.id,
                    credential=credential,
                    status=status,
                    last_checked=datetime.now(),
                )

    async def _validate_and_update_status(self, credential: ModelCredential):
        result = self.validate_fn(credential)
        if asyncio.iscoroutine(result):
            result = await result
        if result:
            await self.update_status(credential, StatusType.ACTIVE)
        else:
            await self.update_status(credential, StatusType.INACTIVE)

    async def _log_status(self):
        log.info(f'当前凭证池状态: {self.model_provider} {self.target_model}')
        for credential in self.credential_pool.values():
            log.info(
                f'{credential.id}: {credential.status}: '
                f'{credential.last_checked.strftime("%Y-%m-%d %H:%M:%S")}'
            )

    async def _health_check(self):
        for credential in self.credential_pool.values():
            if credential.status == StatusType.ACTIVE:
                continue
            await self._validate_and_update_status(credential.credential)
        await self._log_status()

    async def _health_check_loop(self):
        log.info(f'执行首次健康检查: {self.model_provider} {self.target_model}')
        for credential in self.model_credentials:
            await self._validate_and_update_status(credential)
        log.info(f'首次健康检查完成: {self.model_provider} {self.target_model}')
        await self._log_status()

        log.info(
            f'健康检查循环开始, 间隔 {self.health_check_interval} 秒: '
            f'{self.model_provider} {self.target_model}'
        )
        while self._running:
            await asyncio.sleep(self.health_check_interval)
            await self._health_check()

    async def _initialize(self):
        log.info(f'>> Initializing credential pool for {self.target_model}')
        log.info(f'Model credentials count: {len(self.model_credentials)}')
        for credential in self.model_credentials:
            log.info(f'  Adding credential: {credential.id} - {credential.model_name}')
            await self.update_status(credential, StatusType.ACTIVE)
        log.info(f'<< Credential pool size after initialization: {len(self.credential_pool)}')
        log.info(f'凭证池初始化完成: {self.model_provider} {self.target_model}')
        await self._log_status()

    def _cleanup(self):
        credentials = self.credential_pool.values()
        if len(credentials) == 0:
            return
        for credential in credentials:
            del credential
        self.credential_pool = {}
        log.info(f'凭证池清理完成: {self.model_provider} {self.target_model}')

    async def start(self):
        if len(self.model_credentials) == 0:
            return
        self._running = True
        await self._initialize()

        if not agent_settings.run_model_health_check:
            return
        log.info(f'启动后台健康检查任务: {self.model_provider} {self.target_model}')
        self._health_check_task = asyncio.create_task(self._health_check_loop())

    def stop(self):
        self._running = False
        if self._health_check_task is not None:
            self._health_check_task.cancel()
            self._health_check_task = None
        self._cleanup()
