import httpx

limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
timeout = httpx.Timeout(None, connect=5.0)  # 设置时间限制