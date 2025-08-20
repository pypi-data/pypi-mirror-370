from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LogMessage(_message.Message):
    __slots__ = ("level", "msg", "entities", "aliases")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    ALIASES_FIELD_NUMBER: _ClassVar[int]
    level: str
    msg: str
    entities: _containers.RepeatedScalarFieldContainer[str]
    aliases: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, level: _Optional[str] = ..., msg: _Optional[str] = ..., entities: _Optional[_Iterable[str]] = ..., aliases: _Optional[_Iterable[str]] = ...) -> None: ...
