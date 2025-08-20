import common_pb2 as _common_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Processor(_message.Message):
    __slots__ = ("uri", "config", "arguments")
    URI_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    uri: str
    config: str
    arguments: str
    def __init__(self, uri: _Optional[str] = ..., config: _Optional[str] = ..., arguments: _Optional[str] = ...) -> None: ...

class RunnerMessage(_message.Message):
    __slots__ = ("proc", "start", "msg", "close", "streamMsg", "pipeline")
    PROC_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    STREAMMSG_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    proc: Processor
    start: _empty_pb2.Empty
    msg: _common_pb2.Message
    close: _common_pb2.Close
    streamMsg: _common_pb2.StreamMessage
    pipeline: str
    def __init__(self, proc: _Optional[_Union[Processor, _Mapping]] = ..., start: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., msg: _Optional[_Union[_common_pb2.Message, _Mapping]] = ..., close: _Optional[_Union[_common_pb2.Close, _Mapping]] = ..., streamMsg: _Optional[_Union[_common_pb2.StreamMessage, _Mapping]] = ..., pipeline: _Optional[str] = ...) -> None: ...
