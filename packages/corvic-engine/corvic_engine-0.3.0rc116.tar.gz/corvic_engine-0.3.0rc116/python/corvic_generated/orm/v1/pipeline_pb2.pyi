from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChunkPdfPipelineTransformation(_message.Message):
    __slots__ = ("output_name",)
    OUTPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    output_name: str
    def __init__(self, output_name: _Optional[str] = ...) -> None: ...

class OcrPdfPipelineTransformation(_message.Message):
    __slots__ = ("text_output_name", "relationship_output_name", "image_output_name")
    TEXT_OUTPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIP_OUTPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_OUTPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    text_output_name: str
    relationship_output_name: str
    image_output_name: str
    def __init__(self, text_output_name: _Optional[str] = ..., relationship_output_name: _Optional[str] = ..., image_output_name: _Optional[str] = ...) -> None: ...

class SanitizeParquetPipelineTransformation(_message.Message):
    __slots__ = ("output_name",)
    OUTPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    output_name: str
    def __init__(self, output_name: _Optional[str] = ...) -> None: ...

class TableFunctionPassthroughPipelineTransformation(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PipelineTransformation(_message.Message):
    __slots__ = ("chunk_pdf", "ocr_pdf", "sanitize_parquet", "table_function_passthrough", "processed_input_names")
    CHUNK_PDF_FIELD_NUMBER: _ClassVar[int]
    OCR_PDF_FIELD_NUMBER: _ClassVar[int]
    SANITIZE_PARQUET_FIELD_NUMBER: _ClassVar[int]
    TABLE_FUNCTION_PASSTHROUGH_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_INPUT_NAMES_FIELD_NUMBER: _ClassVar[int]
    chunk_pdf: ChunkPdfPipelineTransformation
    ocr_pdf: OcrPdfPipelineTransformation
    sanitize_parquet: SanitizeParquetPipelineTransformation
    table_function_passthrough: TableFunctionPassthroughPipelineTransformation
    processed_input_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, chunk_pdf: _Optional[_Union[ChunkPdfPipelineTransformation, _Mapping]] = ..., ocr_pdf: _Optional[_Union[OcrPdfPipelineTransformation, _Mapping]] = ..., sanitize_parquet: _Optional[_Union[SanitizeParquetPipelineTransformation, _Mapping]] = ..., table_function_passthrough: _Optional[_Union[TableFunctionPassthroughPipelineTransformation, _Mapping]] = ..., processed_input_names: _Optional[_Iterable[str]] = ...) -> None: ...
