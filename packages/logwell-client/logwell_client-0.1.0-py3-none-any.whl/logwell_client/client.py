from .schema import LogCreateSchema, Endpoint
import httpx


class SyncLogClient:
    def __init__(self, base_url: str, api_key: str, tenant: str | None = None):
        self.tenant = tenant
        self.client = httpx.Client(base_url=base_url, headers={"x-API-key": api_key})

    def create_log(
        self, log: LogCreateSchema | dict, endpoint: Endpoint = Endpoint.Blocking
    ) -> dict:
        if self.tenant:
            if isinstance(log, LogCreateSchema):
                log.tenant = self.tenant
            else:
                log["tenant"] = self.tenant

        response = self.client.post(
            endpoint, json=log.model_dump() if isinstance(log, LogCreateSchema) else log
        )
        return response

    def close(self):
        self.client.close()


class AsyncLogClient:
    def __init__(self, base_url: str, api_key: str, tenant: str | None = None):
        self.tenant = tenant
        self.client = httpx.AsyncClient(
            base_url=base_url, headers={"x-API-key": api_key}
        )

    async def create_log(
        self, log: LogCreateSchema | dict, endpoint: Endpoint = Endpoint.Blocking
    ) -> dict:
        if self.tenant:
            if isinstance(log, LogCreateSchema):
                log.tenant = self.tenant
            else:
                log["tenant"] = self.tenant

        response = await self.client.post(
            endpoint, json=log.model_dump() if isinstance(log, LogCreateSchema) else log
        )
        return response

    async def aclose(self):
        await self.client.aclose()
