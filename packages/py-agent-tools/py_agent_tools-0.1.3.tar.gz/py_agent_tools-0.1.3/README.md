# py-agent-tools

A Python package providing tools for working with various AI agents and APIs.

## Installation

```bash
pip install py-agent-tools
```

## Usage

- How to use model switcher with local credentials:

```python
# 服务起来的时候需要加载所有可用的凭证
switcher = ModelSwitcher(allowed_providers=['laozhang'])
await switcher.start_all_pools()

# 通过 model_provider 和 model_name 获取凭证池
model_provider = 'laozhang'
model_name = 'o4-mini'
credential_pool = switcher.get_credential_pool(model_provider, model_name)

# 根据 model_provider 和凭证池创建 agent, 可以设置系统提示词, 模型参数, 以及 http 请求的超时时间
agent= switcher.get_agent_cls(model_provider).create(
    system_prompt='system',
    credential_pool=credential_pool,
    model_settings={'temperature': 0.0},
    timeout=300,
)

# 给定提示词，agent 运行推理并存储结果于 runner 对象里, 支持传入后处理函数, 支持查看 usage 等信息
runner = await agent.run('hello')
print(runner.result)

# 服务关闭的时候清除所有凭证
switcher.stop_all_pools()
```

- TODO: How to use model switcher with remote credential api:

## Features

- Support for multiple AI agent providers
- Unified interface for different APIs
- Credential management
- Model switching capabilities

## Requirements

- Python >= 3.10

## 添加新的凭证

### 非微调模型

- 参考 `*_agent.py`

### 微调模型

- 参考 `*_ft_agent.py`
