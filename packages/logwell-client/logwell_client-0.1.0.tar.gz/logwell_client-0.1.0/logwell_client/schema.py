from pydantic import BaseModel, Field
from enum import StrEnum
from typing import List


class Level(StrEnum):
    INFO = "INFO"
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    NOTSET = "NOTSET"


class LogCreateSchema(BaseModel):
    tenant: str | None = None
    log: dict | str = Field(default_factory=dict)
    execution_path: dict | None = None
    metadata: dict = Field(default_factory=dict)
    tag: str | None = None
    level: Level = Level.NOTSET
    group_path: List[str] | None = None


class Endpoint(StrEnum):
    Blocking = "/logs/"
    NonBlocking = "/logs/non-blocking/"
    BuiltInNonBlocking = "/logs/non-blocking/builtin/"
