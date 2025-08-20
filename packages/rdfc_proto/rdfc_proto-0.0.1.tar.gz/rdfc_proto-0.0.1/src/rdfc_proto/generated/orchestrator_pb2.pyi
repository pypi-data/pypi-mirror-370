import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessorInit(_message.Message):
    __slots__ = ("uri", "error")
    URI_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    uri: str
    error: _common_pb2.Error
    def __init__(self, uri: _Optional[str] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ...) -> None: ...

class Identify(_message.Message):
    __slots__ = ("uri",)
    URI_FIELD_NUMBER: _ClassVar[int]
    uri: str
    def __init__(self, uri: _Optional[str] = ...) -> None: ...

class OrchestratorMessage(_message.Message):
    __slots__ = ("init", "close", "identify", "msg", "streamMsg")
    INIT_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    IDENTIFY_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    STREAMMSG_FIELD_NUMBER: _ClassVar[int]
    init: ProcessorInit
    close: _common_pb2.Close
    identify: Identify
    msg: _common_pb2.Message
    streamMsg: _common_pb2.StreamMessage
    def __init__(self, init: _Optional[_Union[ProcessorInit, _Mapping]] = ..., close: _Optional[_Union[_common_pb2.Close, _Mapping]] = ..., identify: _Optional[_Union[Identify, _Mapping]] = ..., msg: _Optional[_Union[_common_pb2.Message, _Mapping]] = ..., streamMsg: _Optional[_Union[_common_pb2.StreamMessage, _Mapping]] = ...) -> None: ...
