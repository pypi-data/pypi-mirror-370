# Cathay JBS Python SDK

跨项目使用的JBS Python SDK

# 安装

> 版本要求 `python>=3.10`

```bash
pip install jbssdk
```

# 使用

```python
from jbssdk.Client import JBS
import asyncio


async def main():
    jbs = JBS()
    res = await jbs.get_deal_after_info()
```