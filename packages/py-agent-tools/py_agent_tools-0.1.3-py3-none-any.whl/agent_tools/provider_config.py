"""
Provider definitions and enums.
This module contains provider-related enums and constants to avoid circular imports.
"""

from pydantic import BaseModel, Field


class SupportedModel(BaseModel):
    model_provider: str = Field(default="")  # for model relay
    model_name: str = Field(default="")
    ckpt_id: str = Field(default="")
    deployment: str = Field(default="")
    api_version: str = Field(default="")
    model_settings: dict = Field(default_factory=dict)


class AccountCredential(BaseModel):
    account_id: str = Field(default="")
    group_id: str = Field(default="")
    base_url: str = Field(default="")
    api_key: str = Field(default="")
    account_info: dict = Field(default_factory=dict)
    supported_models: list[SupportedModel] = Field(default_factory=list)


class ProviderConfig(BaseModel):
    """
    供应商配置文件定义
    """

    default_models: list[SupportedModel] = Field(default_factory=list)
    accounts: list[AccountCredential] = Field(default_factory=list)
