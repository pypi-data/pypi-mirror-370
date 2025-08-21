import logging
from .client import SyncLogClient, AsyncLogClient
from .schema import LogCreateSchema, Level, Endpoint


class LogServiceHandler(logging.Handler):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        tenant: str | None = None,
        default_endpoint: Endpoint = Endpoint.Blocking,
        async_mode: bool = False,
    ):
        super().__init__()
        self.tenant = tenant
        self.default_endpoint = default_endpoint
        self.async_mode = async_mode
        if async_mode:
            self.client = AsyncLogClient(base_url, api_key, tenant)
        else:
            self.client = SyncLogClient(base_url, api_key, tenant)

    def emit(self, record: logging.LogRecord):
        try:
            log_entry = LogCreateSchema(
                tenant=self.client.tenant,
                log=record.getMessage(),
                execution_path={
                    "filename": record.filename,
                    "funcName": record.funcName,
                    "lineno": record.lineno,
                    "module": record.module,
                    "process": record.process,
                    "thread": record.thread,
                },
                metadata=getattr(record, "metadata", {}),
                level=Level(record.levelname)
                if record.levelname
                else Level.NOTSET.value,
                tag=getattr(record, "tag", None),
                group_path=getattr(record, "group_path", None),
            )

            self.endpoint = (
                record.endpoint
                if hasattr(record, "endpoint")
                else self.default_endpoint
            )

            if self.async_mode:
                import asyncio

                asyncio.create_task(self.client.create_log(log_entry), self.endpoint)
            else:
                self.client.create_log(log_entry, self.endpoint)

        except Exception:
            self.handleError(record)

    def close(self):
        try:
            if self.async_mode:
                import asyncio

                asyncio.run(self.client.aclose())
            else:
                self.client.close()
        finally:
            super().close()
