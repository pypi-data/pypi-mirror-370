from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Error(_message.Message):
    __slots__ = ("cause",)
    CAUSE_FIELD_NUMBER: _ClassVar[int]
    cause: str
    def __init__(self, cause: _Optional[str] = ...) -> None: ...

class Close(_message.Message):
    __slots__ = ("channel",)
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    channel: str
    def __init__(self, channel: _Optional[str] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("channel", "data")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    channel: str
    data: bytes
    def __init__(self, channel: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class Id(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DataChunk(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...

class StreamMessage(_message.Message):
    __slots__ = ("id", "channel")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    id: Id
    channel: str
    def __init__(self, id: _Optional[_Union[Id, _Mapping]] = ..., channel: _Optional[str] = ...) -> None: ...
