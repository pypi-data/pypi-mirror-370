import aiohttp

from tp_helper.proxy_manager_helper.schemas.proxy_schema import ProxySchema


class ProxyManagerHelper:
    def __init__(self, proxy_manager_url: str):
        self.proxy_manager_url = proxy_manager_url
        self.proxy_schema: ProxySchema | None = None

    async def get_one_proxy(self, queue: str) -> ProxySchema:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.proxy_manager_url + "/proxies", params={"queue": queue}
            ) as response:
                proxy_text = await response.text()
                self.proxy_schema = ProxySchema.model_validate_json(proxy_text)
                return self.proxy_schema

    async def get_proxy_url(self, queue: str) -> str:
        await self.get_one_proxy(queue=queue)
        return self.get_http()

    def get_http(self) -> str:
        return f"http://{self.proxy_schema.login}:{self.proxy_schema.password}@{self.proxy_schema.ip}:{self.proxy_schema.port}"
