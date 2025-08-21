from types import credential_descriptor_pb2 as _credential_descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class BookCustomAuthenticationDescriptor(_message.Message):
    __slots__ = ('id', 'credentials', 'description', 'name')
    ID_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    credentials: _containers.RepeatedCompositeFieldContainer[_credential_descriptor_pb2.CredentialDescriptor]
    description: str
    name: str

    def __init__(self, id: _Optional[str]=..., credentials: _Optional[_Iterable[_Union[_credential_descriptor_pb2.CredentialDescriptor, _Mapping]]]=..., description: _Optional[str]=..., name: _Optional[str]=...) -> None:
        ...