# pylint: disable=no-name-in-module
from kognitos.bdk.runtime.client.proto.types.book_procedure_descriptor_pb2 import \
    BookProcedureDescriptor as ProtoBookProcedureDescriptor

# pylint: enable=no-name-in-module
from ..book_procedure_descriptor import BookProcedureDescriptor
from .book_procedure_signature import map_book_procedure_signature
from .concept_descriptor import map_concept_descriptor
from .example_descriptor import map_example_descriptor
from .question_descriptor import map_question_descriptor


def map_book_procedure_descriptor(
    data: ProtoBookProcedureDescriptor,
) -> BookProcedureDescriptor:
    return BookProcedureDescriptor(
        id=data.id,
        short_description=data.short_description,
        long_description=data.long_description,
        signature=map_book_procedure_signature(data.signature),
        inputs=[map_concept_descriptor(cd) for cd in data.inputs],
        outputs=[map_concept_descriptor(cd) for cd in data.outputs],
        questions=[map_question_descriptor(qd) for qd in data.questions],
        filter_capable=data.filter_capable,
        page_capable=data.page_capable,
        connection_required=data.connection_required,
        examples=[map_example_descriptor(example) for example in data.examples],
    )
