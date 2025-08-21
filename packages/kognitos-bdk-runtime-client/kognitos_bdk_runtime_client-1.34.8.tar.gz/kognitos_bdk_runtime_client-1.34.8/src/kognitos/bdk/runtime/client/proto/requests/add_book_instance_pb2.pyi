from requests import labels_pb2 as _labels_pb2
from types import book_custom_authentication_descriptor_pb2 as _book_custom_authentication_descriptor_pb2
from types import concept_value_pb2 as _concept_value_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class AddBookInstanceRequest(_message.Message):
    __slots__ = ('book_name', 'book_version', 'credential', 'config', 'labels')
    BOOK_NAME_FIELD_NUMBER: _ClassVar[int]
    BOOK_VERSION_FIELD_NUMBER: _ClassVar[int]
    CREDENTIAL_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    book_name: str
    book_version: str
    credential: _book_custom_authentication_descriptor_pb2.BookCustomAuthenticationDescriptor
    config: _containers.RepeatedCompositeFieldContainer[_concept_value_pb2.ConceptValue]
    labels: _containers.RepeatedCompositeFieldContainer[_labels_pb2.Label]

    def __init__(self, book_name: _Optional[str]=..., book_version: _Optional[str]=..., credential: _Optional[_Union[_book_custom_authentication_descriptor_pb2.BookCustomAuthenticationDescriptor, _Mapping]]=..., config: _Optional[_Iterable[_Union[_concept_value_pb2.ConceptValue, _Mapping]]]=..., labels: _Optional[_Iterable[_Union[_labels_pb2.Label, _Mapping]]]=...) -> None:
        ...