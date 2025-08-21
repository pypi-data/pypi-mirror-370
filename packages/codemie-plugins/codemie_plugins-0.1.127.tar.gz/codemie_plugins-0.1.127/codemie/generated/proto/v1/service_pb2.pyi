from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Handler(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GET: _ClassVar[Handler]
    RUN: _ClassVar[Handler]

class Puppet(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LANGCHAIN_TOOL: _ClassVar[Puppet]
GET: Handler
RUN: Handler
LANGCHAIN_TOOL: Puppet

class PuppetRequest(_message.Message):
    __slots__ = ("lc_tool",)
    LC_TOOL_FIELD_NUMBER: _ClassVar[int]
    lc_tool: LangChainTool
    def __init__(self, lc_tool: _Optional[_Union[LangChainTool, _Mapping]] = ...) -> None: ...

class PuppetResponse(_message.Message):
    __slots__ = ("lc_tool",)
    LC_TOOL_FIELD_NUMBER: _ClassVar[int]
    lc_tool: LangChainTool
    def __init__(self, lc_tool: _Optional[_Union[LangChainTool, _Mapping]] = ...) -> None: ...

class ServiceMeta(_message.Message):
    __slots__ = ("subject", "handler", "puppet")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    HANDLER_FIELD_NUMBER: _ClassVar[int]
    PUPPET_FIELD_NUMBER: _ClassVar[int]
    subject: str
    handler: Handler
    puppet: Puppet
    def __init__(self, subject: _Optional[str] = ..., handler: _Optional[_Union[Handler, str]] = ..., puppet: _Optional[_Union[Puppet, str]] = ...) -> None: ...

class ServiceRequest(_message.Message):
    __slots__ = ("meta", "puppet_request")
    META_FIELD_NUMBER: _ClassVar[int]
    PUPPET_REQUEST_FIELD_NUMBER: _ClassVar[int]
    meta: ServiceMeta
    puppet_request: PuppetRequest
    def __init__(self, meta: _Optional[_Union[ServiceMeta, _Mapping]] = ..., puppet_request: _Optional[_Union[PuppetRequest, _Mapping]] = ...) -> None: ...

class ServiceResponse(_message.Message):
    __slots__ = ("meta", "puppet_response", "error")
    META_FIELD_NUMBER: _ClassVar[int]
    PUPPET_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    meta: ServiceMeta
    puppet_response: PuppetResponse
    error: str
    def __init__(self, meta: _Optional[_Union[ServiceMeta, _Mapping]] = ..., puppet_response: _Optional[_Union[PuppetResponse, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class LangChainTool(_message.Message):
    __slots__ = ("name", "description", "args_schema", "result", "error", "query")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ARGS_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    args_schema: str
    result: str
    error: str
    query: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., args_schema: _Optional[str] = ..., result: _Optional[str] = ..., error: _Optional[str] = ..., query: _Optional[str] = ...) -> None: ...
