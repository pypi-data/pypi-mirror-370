"""Protocols defining the way corvic interacts with the platform."""

from typing import Final

from corvic.system._dimension_reduction import (
    DimensionReducer,
    TruncateDimensionReducer,
    UmapDimensionReducer,
)
from corvic.system._embedder import (
    ClipText,
    EmbedImageContext,
    EmbedImageResult,
    EmbedTextContext,
    EmbedTextResult,
    ImageEmbedder,
    SigLIP2Text,
    TextEmbedder,
)
from corvic.system._image_embedder import (
    Clip,
    CombinedImageEmbedder,
    IdentityImageEmbedder,
    RandomImageEmbedder,
    SigLIP2,
    image_from_bytes,
)
from corvic.system._planner import OpGraphPlanner, ValidateFirstExecutor
from corvic.system._text_embedder import IdentityTextEmbedder, RandomTextEmbedder
from corvic.system.client import Client
from corvic.system.in_memory_executor import (
    InMemoryExecutionResult,
    InMemoryExecutor,
    get_polars_embedding,
    get_polars_embedding_length,
    make_dict_bytes_human_readable,
    make_list_bytes_human_readable,
)
from corvic.system.op_graph_executor import (
    ExecutionContext,
    ExecutionResult,
    OpGraphExecutor,
    TableComputeContext,
    TableComputeResult,
    TableSliceArgs,
)
from corvic.system.staging import StagingDB, VectorSimilarityMetric
from corvic.system.storage import (
    Blob,
    BlobClient,
    Bucket,
    DataMisplacedError,
    StorageManager,
)

DEFAULT_VECTOR_COLUMN_NAMES_TO_SIZES: Final = {
    "2_dim_vector": 2,
    "3_dim_vector": 3,
    "8_dim_vector": 8,
    "16_dim_vector": 16,
    "32_dim_vector": 32,
    "64_dim_vector": 64,
    "128_dim_vector": 128,
}

__all__ = [
    "Blob",
    "BlobClient",
    "Bucket",
    "Client",
    "Clip",
    "ClipText",
    "CombinedImageEmbedder",
    "DEFAULT_VECTOR_COLUMN_NAMES_TO_SIZES",
    "DataMisplacedError",
    "DimensionReducer",
    "EmbedImageContext",
    "EmbedImageResult",
    "EmbedTextContext",
    "EmbedTextResult",
    "ExecutionContext",
    "ExecutionResult",
    "IdentityImageEmbedder",
    "IdentityTextEmbedder",
    "ImageEmbedder",
    "InMemoryExecutionResult",
    "InMemoryExecutor",
    "OpGraphExecutor",
    "OpGraphPlanner",
    "RandomImageEmbedder",
    "RandomTextEmbedder",
    "SigLIP2",
    "SigLIP2Text",
    "StagingDB",
    "StorageManager",
    "TableComputeContext",
    "TableComputeResult",
    "TableSliceArgs",
    "TextEmbedder",
    "TruncateDimensionReducer",
    "UmapDimensionReducer",
    "ValidateFirstExecutor",
    "VectorSimilarityMetric",
    "get_polars_embedding",
    "get_polars_embedding_length",
    "image_from_bytes",
    "make_dict_bytes_human_readable",
    "make_list_bytes_human_readable",
]
