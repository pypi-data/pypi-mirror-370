# LogWell-client

## Introduction
LogWell-client is a hassle-free Python client to send logs to an instance of [LogWell-service](https://github.com/amirberenji1995/logWell).  
LogWell-client is for you, if you are determined to use LogWell-service to stash your logs and want to avoid plain HTTP calls every now and then throughout your code base.

## Features
1. **Sync and Async clients** for log creation
2. **Blocking and Non-blocking** log creation support
3. Compatible with Python’s built-in `logging` module through a custom handler

## Installation



## Log Schema

A log object in the client follows the same type (`pydantic.BaseModel`) and structure as the service, except for the `uid` and `created_at` fields that are generated automatically at the server upon receiving a log instance; therefore, from LogWell-client perspective, a log consists of the following fields:

```python
tenant: str | None = None                                       # an identifier to the creator (service) of the log
log: dict | str = Field(default_factory=dict)                   # the actual log to save
execution_path: dict | None = None                              # the execution path, leading to where the log is introduced
metadata: dict = Field(default_factory=dict)                    # additional metadata to stroe
tag: str | None = None                                          # a custom tag to query a log or a family of logs
level: Level = Level.NOTSET                                     # the level to produce the log; available options are: ["INFO", "TRACE","DEBUG", "WARNING", "ERROR", "CRITICAL", "FATAL", "NOTSET",]
group_path: List[str] | None = None                             # a group path, to register nnested logs
```

## Log creation approaches
LogWell-service supports log creation through the following approaches:
   - **Naive (blocking) log creation**: LogWell-service keeps the HTTP connection open, while writing the log to the database.
   - **Non-blocking log creation using FastAPI builting BackgroundTasks**: This way, LogWell-service closes the HTTP connection ASAP and afterwards, the log creation is done as an instance of `FastAPI.BackgroundTasks`.
   - **Advanced non-blocking**: In this case, LogWell-service uses a message queue and a celery worker to queue the log as a message and a spearate celery worker takes care of writing it to the database.

In LogWell-client, the log creation approach is specified using the following `StrEnum`:

```python
class Endpoint(StrEnum):
    Blocking = "/logs/"
    NonBlocking = "/logs/non-blocking/"
    BuiltInNonBlocking = "/logs/non-blocking/builtin/"
```


## Usage options
LogWell-client can be either used at client-level or as a custom handler to be added to an instance of `logging.Logger`. Each of these approaches are discussed separately:

### 1. Using client(s either sync or async)

  - #### Synchronous client:
    ```python
    from log_writing_client.src.client import SyncLogClient
    from log_writing_client.src.schema import LogCreateSchema

    client = SyncLogClient(base_url="http://localhost:8000/", api_key="key1", tenant="tenant1")

    response = client.create_log(
        log=LogCreateSchema(
            log="hello world",
            metadata={"client_ip": "127.0.0.1"},
            level="INFO",
            tag="tag1",
        )
    )

    print(response.json())
    client.close()

    >>> OUTPUT:
    {'message': 'Log added successfully', 'data': {'tenant': 'tenant1', 'log': 'hello world', 'execution_path': None, 'metadata': {'client_ip': '127.0.0.1'}, 'tag': 'tag1', 'level': 'INFO', 'group_path': None, 'uid': '680a28ad-88fd-456a-ac81-6d3c42334f33', 'created_at': '2025-08-20T11:21:28.914545'}}
    ```

- #### Asynchronous client:
    ```python
    import asyncio
    from log_writing_client.src.client import AsyncLogClient, Endpoint
    from log_writing_client.src.schema import LogCreateSchema

    async def main():
        client = AsyncLogClient(base_url="http://localhost:8000/", api_key="key1", tenant="tenant1")
        response = await client.create_log(
            log=LogCreateSchema(
                log="hello async world",
                metadata={"client_ip": "127.0.0.1"},
                level="INFO",
                tag="tag2",
            )
        )
        print(response.json())
        await client.aclose()

    asyncio.run(main())

    >>> OUTPUT:
    {'message': 'Log added successfully', 'data': {'tenant': 'tenant1', 'log': 'hello async world', 'execution_path': None, 'metadata': {'client_ip': '127.0.0.1'}, 'tag': 'tag2', 'level': 'INFO', 'group_path': None, 'uid': '420f3c26-8474-4fe9-a7ff-10ad6683ee38', 'created_at': '2025-08-20T11:22:31.195423'}}
    ```

### 2. Using the Logging Handler

LogWell-client also provides a `logging.Handler` implementation to seamlessly integrate with Python logging:

```python
import logging
from log_writing_client.src.handler import LogServiceHandler

logger = logging.getLogger("my-app")
logger.setLevel(logging.DEBUG)

handler = LogServiceHandler(
    base_url="http://localhost:8000",
    api_key="key1",
    tenant="tenant1",
)
logger.addHandler(handler)

logger.info(
    "Hello world!",
    extra={
        "metadata": {"client_ip": "127.0.0.1"},
        "tag": "tag1",
    },
)
```
