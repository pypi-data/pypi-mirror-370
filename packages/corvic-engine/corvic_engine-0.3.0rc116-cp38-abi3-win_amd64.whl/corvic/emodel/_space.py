"""Spaces."""

from __future__ import annotations

import abc
import copy
import datetime
import uuid
from collections.abc import Iterable, Mapping, Sequence
from typing import Final, Literal, Self, TypeAlias, cast

import pyarrow as pa
from sqlalchemy import orm as sa_orm
from sqlalchemy.orm.interfaces import LoaderOption

from corvic import eorm, op_graph, system
from corvic.emodel._base_model import StandardModel
from corvic.emodel._feature_view import FeatureView, FeatureViewEdgeTableMetadata
from corvic.emodel._proto_orm_convert import (
    space_delete_orms,
    space_orm_to_proto,
    space_proto_to_orm,
)
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic.table import Table
from corvic_generated.algorithm.graph.v1 import graph_pb2
from corvic_generated.embedding.v1 import models_pb2 as embedding_models_pb2
from corvic_generated.model.v1alpha import models_pb2
from corvic_generated.orm.v1 import space_pb2

FeatureViewID: TypeAlias = eorm.FeatureViewID
RoomID: TypeAlias = eorm.RoomID
SpaceID: TypeAlias = eorm.SpaceID

_DEFAULT_CONCAT_SEPARATOR = " "
_DEFAULT_CONCAT_LIST_SEPARATOR = ", "


embedding_model_proto_to_name: Final[dict[embedding_models_pb2.Model, str]] = {
    embedding_models_pb2.MODEL_CUSTOM: system.RandomTextEmbedder.model_name(),
    embedding_models_pb2.MODEL_SENTENCE_TRANSFORMER: "text-embedding-004",
    embedding_models_pb2.MODEL_GCP_TEXT_EMBEDDING_004: "text-embedding-004",
    embedding_models_pb2.MODEL_OPENAI_TEXT_EMBEDDING_3_SMALL: "text-embedding-3-small",
    embedding_models_pb2.MODEL_OPENAI_TEXT_EMBEDDING_3_LARGE: "text-embedding-3-large",
    embedding_models_pb2.MODEL_IDENTITY: system.IdentityTextEmbedder.model_name(),
    embedding_models_pb2.MODEL_UNSPECIFIED: "",
    embedding_models_pb2.MODEL_CLIP: system.ClipText.model_name(),
    embedding_models_pb2.MODEL_SIGLIP2: system.SigLIP2Text.model_name(),
}
name_to_proto_embedding_model = {
    name: model for model, name in embedding_model_proto_to_name.items()
}


def image_model_proto_to_name(image_model: embedding_models_pb2.ImageModel):
    match image_model:
        case embedding_models_pb2.IMAGE_MODEL_CUSTOM:
            return Ok(system.RandomImageEmbedder.model_name())
        case embedding_models_pb2.IMAGE_MODEL_CLIP:
            return Ok(system.Clip.model_name())
        case embedding_models_pb2.IMAGE_MODEL_IDENTITY:
            return Ok(system.IdentityImageEmbedder.model_name())
        case embedding_models_pb2.IMAGE_MODEL_SIGLIP2:
            return Ok(system.SigLIP2.model_name())
        case embedding_models_pb2.IMAGE_MODEL_UNSPECIFIED:
            return Ok("")
        case _:
            return NotFoundError("Could not find image model")


def image_model_can_embed_text(image_model: embedding_models_pb2.ImageModel):
    match image_model:
        case embedding_models_pb2.IMAGE_MODEL_CUSTOM:
            return Ok(value=True)
        case embedding_models_pb2.IMAGE_MODEL_CLIP:
            return Ok(value=True)
        case embedding_models_pb2.IMAGE_MODEL_IDENTITY:
            return Ok(value=True)
        case embedding_models_pb2.IMAGE_MODEL_SIGLIP2:
            return Ok(value=True)
        case embedding_models_pb2.IMAGE_MODEL_UNSPECIFIED:
            return Ok(value=False)
        case _:
            return NotFoundError("Could not find image model")


def image_model_can_embed_images(image_model: embedding_models_pb2.ImageModel):
    match image_model:
        case embedding_models_pb2.IMAGE_MODEL_CUSTOM:
            return Ok(value=True)
        case embedding_models_pb2.IMAGE_MODEL_CLIP:
            return Ok(value=True)
        case embedding_models_pb2.IMAGE_MODEL_IDENTITY:
            return Ok(value=True)
        case embedding_models_pb2.IMAGE_MODEL_SIGLIP2:
            return Ok(value=True)
        case embedding_models_pb2.IMAGE_MODEL_UNSPECIFIED:
            return Ok(value=False)
        case _:
            return NotFoundError("Could not find image model")


def _image_model_proto_to_name_unsafe(model: embedding_models_pb2.ImageModel):
    match image_model_proto_to_name(model):
        case Ok(value):
            return value
        case err:
            raise err


name_to_proto_image_model = {
    _image_model_proto_to_name_unsafe(
        cast(embedding_models_pb2.ImageModel, model)
    ): cast(embedding_models_pb2.ImageModel, model)
    for model in embedding_models_pb2.ImageModel.values()
}


class Space(StandardModel[SpaceID, models_pb2.Space, eorm.Space]):
    """Spaces apply embedding methods to FeatureViews.

    Example:
    >>> space = Space.node2vec(feature_view, dim=10, walk_length=10, window=10)
    """

    @classmethod
    def orm_class(cls):
        return eorm.Space

    @classmethod
    def id_class(cls):
        return SpaceID

    @classmethod
    async def _orm_to_proto(cls, orm_obj: eorm.Space) -> models_pb2.Space:
        return await space_orm_to_proto(orm_obj)

    @classmethod
    async def _proto_to_orm(
        cls, proto_obj: models_pb2.Space, session: eorm.Session
    ) -> Ok[eorm.Space] | InvalidArgumentError:
        return await space_proto_to_orm(proto_obj, session)

    @classmethod
    async def delete_by_ids(
        cls, ids: Sequence[SpaceID], session: eorm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return await space_delete_orms(ids, session)

    @classmethod
    def orm_load_options(cls) -> list[LoaderOption]:
        return [
            sa_orm.selectinload(eorm.Space.feature_view)
            .selectinload(eorm.FeatureView.feature_view_sources)
            .selectinload(eorm.FeatureViewSource.source)
            .selectinload(eorm.Source.pipeline_ref)
        ]

    @property
    def name(self):
        return self.proto_self.name

    @property
    def description(self):
        return self.proto_self.description

    @property
    def feature_view(self) -> FeatureView:
        return FeatureView.from_proto(
            proto=self.proto_self.feature_view,
            client=self.client,
        )

    @property
    def auto_sync(self):
        return self.proto_self.auto_sync

    def with_auto_sync(self, *, auto_sync: bool):
        self.proto_self.auto_sync = auto_sync
        return self

    @abc.abstractmethod
    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        """Generate per-output-source embeddings tables for this space."""

    @classmethod
    def create_specific(
        cls,
        *,
        name: str,
        description: str,
        feature_view: FeatureView,
        parameters: SpecificSpaceParameters,
        room_id: RoomID,
        auto_sync: bool = False,
        client: system.Client,
    ) -> Ok[SpecificSpace] | InvalidArgumentError:
        client = client or feature_view.client
        room_id = room_id or feature_view.room_id
        if room_id != feature_view.room_id:
            return InvalidArgumentError("room id must match feature_view room id")
        match parameters:
            case Node2VecParameters():
                return RelationalSpace.create(
                    name=name,
                    description=description,
                    feature_view=feature_view,
                    parameters=parameters,
                    room_id=room_id,
                    auto_sync=auto_sync,
                    client=client,
                )
            case ConcatAndEmbedParameters():
                return SemanticSpace.create(
                    name=name,
                    description=description,
                    feature_view=feature_view,
                    parameters=parameters,
                    room_id=room_id,
                    auto_sync=auto_sync,
                    client=client,
                )
            case EmbedAndConcatParameters():
                return TabularSpace.create(
                    name=name,
                    description=description,
                    feature_view=feature_view,
                    parameters=parameters,
                    room_id=room_id,
                    auto_sync=auto_sync,
                    client=client,
                )
            case EmbedImageParameters():
                return ImageSpace.create(
                    name=name,
                    description=description,
                    feature_view=feature_view,
                    parameters=parameters,
                    room_id=room_id,
                    auto_sync=auto_sync,
                    client=client,
                )

    def with_name(self, name: str):
        proto_self = copy.copy(self.proto_self)
        proto_self.name = name
        return Ok(
            self.__class__(
                proto_self=proto_self,
                client=self.client,
            )
        )

    def with_description(self, description: str):
        proto_self = copy.copy(self.proto_self)
        proto_self.description = description
        return Ok(
            self.__class__(
                proto_self=proto_self,
                client=self.client,
            )
        )

    @classmethod
    async def from_id(
        cls,
        *,
        space_id: SpaceID,
        session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[SpecificSpace] | NotFoundError:
        return (
            await cls.load_proto_for(
                obj_id=space_id,
                existing_session=session,
                client=client,
            )
        ).map(
            lambda proto_self: cls.from_proto(
                proto=proto_self,
                client=client,
            )
        )

    @classmethod
    async def list(
        cls,
        *,
        limit: int | None = None,
        room_id: eorm.RoomID | None = None,
        created_before: datetime.datetime | None = None,
        ids: Iterable[eorm.SpaceID] | None = None,
        existing_session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[SpecificSpace]] | InvalidArgumentError | NotFoundError:
        match await cls.list_as_proto(
            client=client,
            limit=limit,
            room_id=room_id,
            created_before=created_before,
            ids=ids,
            existing_session=existing_session,
        ):
            case NotFoundError() | InvalidArgumentError() as err:
                return err
            case Ok(protos):
                return Ok([cls.from_proto(proto, client=client) for proto in protos])

    @classmethod
    def from_proto(
        cls, proto: models_pb2.Space, client: system.Client
    ) -> SpecificSpace:
        if proto.space_parameters.HasField("node2vec_parameters"):
            return RelationalSpace(
                proto_self=proto,
                client=client,
            )
        if proto.space_parameters.HasField("concat_and_embed_parameters"):
            return SemanticSpace(
                proto_self=proto,
                client=client,
            )
        if proto.space_parameters.HasField("embed_and_concat_parameters"):
            return TabularSpace(
                proto_self=proto,
                client=client,
            )
        if proto.space_parameters.HasField("embed_image_parameters"):
            return ImageSpace(
                proto_self=proto,
                client=client,
            )
        return UnknownSpace(
            proto_self=proto,
            client=client,
        )


class UnknownSpace(Space):
    """A space that this version of the code doesn't know what to do with."""

    @classmethod
    def create(cls, *, feature_view: FeatureView, client: system.Client):
        client = client or feature_view.client
        return cls(
            proto_self=models_pb2.Space(
                feature_view=feature_view.proto_self,
            ),
            client=client,
        )

    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        """Generate per-ouput-source embeddings tables for this space."""
        return Ok({})


class Node2VecParameters:
    proto_self: Final[graph_pb2.Node2VecParameters]

    def __init__(self, proto_self: graph_pb2.Node2VecParameters):
        self.proto_self = proto_self

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        dim: int = 10,
        walk_length: int = 10,
        window: int = 10,
        p: float = 1.0,
        q: float = 1.0,
        alpha: float = 0.025,
        min_alpha: float = 0.0001,
        negative: int = 5,
        epochs: int = 10,
    ):
        return cls(
            graph_pb2.Node2VecParameters(
                ndim=dim,
                walk_length=walk_length,
                window=window,
                p=p,
                q=q,
                alpha=alpha,
                min_alpha=min_alpha,
                negative=negative,
                epochs=epochs,
            )
        )

    @property
    def dim(self) -> int:
        return self.proto_self.ndim

    @property
    def walk_length(self) -> int:
        return self.proto_self.walk_length

    @property
    def window(self) -> int:
        return self.proto_self.window

    @property
    def p(self) -> float:
        return self.proto_self.p

    @property
    def q(self) -> float:
        return self.proto_self.q

    @property
    def alpha(self) -> float:
        return self.proto_self.alpha

    @property
    def min_alpha(self) -> float:
        return self.proto_self.min_alpha

    @property
    def negative(self) -> int:
        return self.proto_self.negative

    @property
    def epochs(self) -> int:
        return self.proto_self.epochs


class RelationalSpace(Space):
    """Spaces for embeddings that encode relationships."""

    @property
    def parameters(self) -> Node2VecParameters:
        return Node2VecParameters(self.proto_self.space_parameters.node2vec_parameters)

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: str,
        feature_view: FeatureView,
        parameters: Node2VecParameters,
        client: system.Client,
        room_id: eorm.RoomID,
        auto_sync: bool = False,
    ) -> Ok[RelationalSpace] | InvalidArgumentError:
        if not feature_view.relationships:
            return InvalidArgumentError(
                "space will not be useful without at least one relationship"
            )
        if not feature_view.output_sources:
            return InvalidArgumentError(
                "space will not be useful without at least one output source"
            )
        proto_self = models_pb2.Space(
            name=name,
            description=description,
            auto_sync=auto_sync,
            feature_view=feature_view.proto_self,
            room_id=str(room_id),
            space_parameters=space_pb2.SpaceParameters(
                node2vec_parameters=parameters.proto_self
            ),
        )

        return Ok(
            RelationalSpace(
                proto_self=proto_self,
                client=client,
            )
        )

    def legacy_embeddings_table(self) -> Ok[Table] | InvalidArgumentError:
        feature_view = self.feature_view

        def gen_edge_list_tables():
            for edge_table in feature_view.output_edge_tables():
                endpoint_metadata = edge_table.get_typed_metadata(
                    FeatureViewEdgeTableMetadata
                )
                yield op_graph.EdgeListTable(
                    table=edge_table.set_metadata({}).op_graph,
                    start_column_name=endpoint_metadata.start_source_column_name,
                    start_entity_name=endpoint_metadata.start_source_name,
                    end_column_name=endpoint_metadata.end_source_column_name,
                    end_entity_name=endpoint_metadata.end_source_name,
                )

        edge_list_tables = list(gen_edge_list_tables())
        if not edge_list_tables:
            return InvalidArgumentError(
                "no relationships given, or those given did not result in edges between"
                + "output sources"
            )

        return op_graph.op.embed_node2vec_from_edge_lists(
            edge_list_tables=edge_list_tables,
            params=self.parameters.proto_self,
        ).map(
            lambda t: Table.from_ops(
                self.client,
                t,
            )
        )

    def _split_embedding_table_by_source(
        self, embeddings_table: op_graph.Op
    ) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        match embeddings_table.unnest_struct("id"):
            case InvalidArgumentError() as err:
                return err
            case Ok(embeddings_table):
                pass
        feature_view = self.feature_view
        id_fields = [
            field
            for field in embeddings_table.schema
            if field.name.startswith("column_")
        ]
        id_fields.sort(key=lambda field: int(field.name.removeprefix("column_")))
        source_name_column = id_fields[-1].name
        dtype_to_id_field = {field.dtype: field.name for field in id_fields[:-1]}

        tables: Mapping[str, Table] = {}
        for source in feature_view.output_sources:
            primary_key_field = source.table.schema.get_primary_key()
            if primary_key_field is None:
                return InvalidArgumentError(
                    "source is required to have a primary key to be an output"
                )
            source_id_column = dtype_to_id_field[primary_key_field.dtype]

            match (
                embeddings_table.filter_rows(
                    op_graph.row_filter.eq(source_name_column, source.name, pa.string())
                )
                .and_then(
                    lambda t, source_id_column=source_id_column: t.select_columns(
                        [source_id_column, "embedding"]
                    )
                )
                .and_then(
                    lambda t, source_id_column=source_id_column: t.rename_columns(
                        {source_id_column: "entity_id"}
                    )
                )
                .and_then(
                    lambda t, source_id=source.id: t.add_literal_column(
                        "source_id",
                        str(source_id),
                        pa.string(),
                    )
                )
            ):
                case Ok(op):
                    pass
                case InvalidArgumentError() as err:
                    return err

            table = Table.from_ops(
                self.client,
                op,
            )
            tables[source.name] = table

        return Ok(tables)

    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        return self.legacy_embeddings_table().and_then(
            lambda t: self._split_embedding_table_by_source(t.op_graph)
        )


class ConcatAndEmbedParameters:
    proto_self: Final[embedding_models_pb2.ConcatAndEmbedParameters]

    def __init__(self, proto_self: embedding_models_pb2.ConcatAndEmbedParameters):
        self.proto_self = proto_self

    @classmethod
    def create(
        cls, column_names: Sequence[str], model_name: str, expected_vector_length: int
    ):
        return cls(
            embedding_models_pb2.ConcatAndEmbedParameters(
                column_names=column_names,
                model_parameters=embedding_models_pb2.Parameters(
                    model=name_to_proto_embedding_model.get(
                        model_name, embedding_models_pb2.MODEL_UNSPECIFIED
                    ),
                    ndim=expected_vector_length,
                ),
            )
        )

    @property
    def model_name(self) -> str:
        return embedding_model_proto_to_name[self.proto_self.model_parameters.model]

    @property
    def column_names(self) -> Sequence[str]:
        return self.proto_self.column_names

    @property
    def expected_vector_length(self) -> int:
        return self.proto_self.model_parameters.ndim


class SemanticSpace(Space):
    """Spaces for embedding source properties."""

    @property
    def parameters(self) -> ConcatAndEmbedParameters:
        return ConcatAndEmbedParameters(
            self.proto_self.space_parameters.concat_and_embed_parameters
        )

    @property
    def expected_coordinate_bitwidth(self) -> Literal[32]:
        return 32

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: str,
        feature_view: FeatureView,
        parameters: ConcatAndEmbedParameters,
        room_id: eorm.RoomID,
        auto_sync: bool = False,
        client: system.Client,
    ) -> Ok[SemanticSpace] | InvalidArgumentError:
        client = client or feature_view.client
        if len(feature_view.output_sources) == 0:
            return InvalidArgumentError(
                "feature view must have at least one output source"
            )
        proto_self = models_pb2.Space(
            name=name,
            description=description,
            auto_sync=auto_sync,
            feature_view=feature_view.proto_self,
            room_id=str(room_id),
            space_parameters=space_pb2.SpaceParameters(
                concat_and_embed_parameters=parameters.proto_self
            ),
        )
        return Ok(
            SemanticSpace(
                proto_self=proto_self,
                client=client,
            )
        )

    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        params = self.parameters
        model_name = params.model_name
        output_sources = self.feature_view.output_sources
        combined_column_tmp_name = f"__concat-{uuid.uuid4()}"
        embedding_column_tmp_name = f"__embed-{uuid.uuid4()}"

        tables: Mapping[str, Table] = {}

        first_schema = output_sources[0].table.schema

        for output_source in output_sources:
            pk_field = output_source.table.schema.get_primary_key()
            if pk_field is None:
                return InvalidArgumentError("output source must have a primary key")

            if first_schema != output_source.table.schema:
                return InvalidArgumentError(
                    "schema for all output sources must be the same"
                )

            op = (
                output_source.table.op_graph.concat_string(
                    column_names=list(params.column_names),
                    combined_column_name=combined_column_tmp_name,
                    separator=_DEFAULT_CONCAT_SEPARATOR,
                    list_separator=_DEFAULT_CONCAT_LIST_SEPARATOR,
                )
                .and_then(
                    lambda t: t.embed_column(
                        combined_column_tmp_name,
                        embedding_column_tmp_name,
                        model_name,
                        "",
                        params.expected_vector_length,
                        self.expected_coordinate_bitwidth,
                    )
                )
                .and_then(
                    lambda t,
                    pk_field=pk_field,
                    embedding_column_tmp_name=embedding_column_tmp_name: t.select_columns(  # noqa: E501
                        [pk_field.name, embedding_column_tmp_name]
                    )
                )
                .and_then(
                    lambda t,
                    pk_field=pk_field,
                    embedding_column_tmp_name=embedding_column_tmp_name: t.rename_columns(  # noqa: E501
                        {
                            pk_field.name: "entity_id",
                            embedding_column_tmp_name: "embedding",
                        }
                    )
                )
                .and_then(
                    lambda t, output_source=output_source: t.add_literal_column(
                        "source_id",
                        str(output_source.id),
                        pa.string(),
                    )
                )
            )

            match op:
                case Ok(table):
                    pass
                case InvalidArgumentError() as err:
                    return err

            tables[output_source.name] = Table.from_ops(self.client, table)

        return Ok(tables)


class EmbedAndConcatParameters:
    proto_self: Final[embedding_models_pb2.EmbedAndConcatParameters]

    def __init__(self, proto_self: embedding_models_pb2.EmbedAndConcatParameters):
        self.proto_self = proto_self

    @classmethod
    def create(cls, column_names: Sequence[str], expected_vector_length: int):
        return cls(
            embedding_models_pb2.EmbedAndConcatParameters(
                column_names=column_names,
                ndim=expected_vector_length,
            )
        )

    @property
    def column_names(self) -> Sequence[str]:
        return self.proto_self.column_names

    @property
    def expected_vector_length(self) -> int:
        return self.proto_self.ndim


class TabularSpace(Space):
    """Spaces for embedding source properties."""

    @property
    def parameters(self) -> EmbedAndConcatParameters:
        return EmbedAndConcatParameters(
            self.proto_self.space_parameters.embed_and_concat_parameters
        )

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: str,
        feature_view: FeatureView,
        parameters: EmbedAndConcatParameters,
        room_id: eorm.RoomID,
        auto_sync: bool = False,
        client: system.Client,
    ) -> Ok[Self] | InvalidArgumentError:
        client = client or feature_view.client
        if len(feature_view.output_sources) == 0:
            return InvalidArgumentError(
                "feature view must have at least one output source"
            )
        proto_self = models_pb2.Space(
            name=name,
            description=description,
            auto_sync=auto_sync,
            feature_view=feature_view.proto_self,
            room_id=str(room_id),
            space_parameters=space_pb2.SpaceParameters(
                embed_and_concat_parameters=parameters.proto_self
            ),
        )
        return Ok(cls(proto_self=proto_self, client=client))

    def embeddings_tables(  # noqa: C901, PLR0915
        self,
    ) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        output_sources = self.feature_view.output_sources
        parameters = self.parameters

        tables: Mapping[str, Table] = {}
        first_schema = output_sources[0].table.schema

        for output_source in output_sources:
            pk_field = output_source.table.schema.get_primary_key()
            if not pk_field:
                return InvalidArgumentError("output source must have a primary key")

            if first_schema != output_source.table.schema:
                return InvalidArgumentError(
                    "schema for all output sources must be the same"
                )

            schema = output_source.table.op_graph.schema
            op = output_source.table.op_graph
            embedding_column_tmp_names: list[str] = []
            for column_name in parameters.proto_self.column_names:
                column = schema.get(column_name)
                if column is None:
                    return InvalidArgumentError("column not found")
                if column.ftype.is_excluded:
                    continue

                match column.ftype:
                    case op_graph.feature_type.Numerical():
                        encoded_column_name = f"__encoded-{uuid.uuid4()}"
                        embedding_column_tmp_names.append(encoded_column_name)
                        match op.encode_columns(
                            encoded_columns=[
                                op_graph.encoder.EncodedColumn(
                                    column_name=column.name,
                                    encoded_column_name=encoded_column_name,
                                    encoder=op_graph.encoder.max_abs_scaler(),
                                )
                            ]
                        ):
                            case Ok(op):
                                pass
                            case InvalidArgumentError() as err:
                                return err
                    case op_graph.feature_type.Categorical():
                        encoded_column_name = f"__encoded-{uuid.uuid4()}"
                        embedding_column_tmp_names.append(encoded_column_name)
                        match op.encode_columns(
                            [
                                op_graph.encoder.EncodedColumn(
                                    column_name=column.name,
                                    encoded_column_name=encoded_column_name,
                                    encoder=op_graph.encoder.label_encoder(),
                                ),
                            ]
                        ):
                            case Ok(op):
                                pass
                            case InvalidArgumentError() as err:
                                return err
                    case op_graph.feature_type.Timestamp():
                        encoded_column_name = f"__encoded-{uuid.uuid4()}"
                        embedding_column_tmp_names.append(encoded_column_name)
                        match op.encode_columns(
                            [
                                op_graph.encoder.EncodedColumn(
                                    column_name=column.name,
                                    encoded_column_name=encoded_column_name,
                                    encoder=op_graph.encoder.timestamp_encoder(),
                                )
                            ]
                        ):
                            case Ok(op):
                                pass
                            case InvalidArgumentError() as err:
                                return err
                    case op_graph.feature_type.Text():
                        encoded_column_name = f"__encoded-{uuid.uuid4()}"
                        embedding_column_tmp_names.append(encoded_column_name)
                        match op.encode_columns(
                            [
                                op_graph.encoder.EncodedColumn(
                                    column_name=column.name,
                                    encoded_column_name=encoded_column_name,
                                    encoder=op_graph.encoder.text_encoder(),
                                )
                            ]
                        ):
                            case Ok(op):
                                pass
                            case InvalidArgumentError() as err:
                                return err
                    case _:
                        continue

            embedding_column_tmp_name = f"__embed-{uuid.uuid4()}"

            # Avoid 0 padding for spaces with small numbers of columns
            target_list_length = min(
                parameters.expected_vector_length, len(embedding_column_tmp_names)
            )

            def reduce_dimension(
                op: op_graph.Op,
                embedding_column_tmp_name=embedding_column_tmp_name,
                target_list_length=target_list_length,
            ):
                return op.truncate_list(
                    list_column_name=embedding_column_tmp_name,
                    target_list_length=target_list_length,
                    padding_value=0,
                )

            def select_columns(
                op: op_graph.Op,
                pk_field=pk_field,
                embedding_column_tmp_name=embedding_column_tmp_name,
            ):
                return op.select_columns([pk_field.name, embedding_column_tmp_name])

            def update_feature_types(
                op: op_graph.Op,
                embedding_column_tmp_name=embedding_column_tmp_name,
            ):
                return op.update_feature_types(
                    {embedding_column_tmp_name: op_graph.feature_type.embedding()}
                )

            def rename_columns(
                op: op_graph.Op,
                pk_field=pk_field,
                embedding_column_tmp_name=embedding_column_tmp_name,
            ):
                return op.rename_columns(
                    {
                        pk_field.name: "entity_id",
                        embedding_column_tmp_name: "embedding",
                    }
                )

            def add_literal_column(
                op: op_graph.Op,
                output_source=output_source,
            ):
                return op.add_literal_column(
                    "source_id",
                    str(output_source.id),
                    pa.string(),
                )

            if len(embedding_column_tmp_names):
                op = op.concat_list(
                    column_names=embedding_column_tmp_names,
                    concat_list_column_name=embedding_column_tmp_name,
                ).and_then(reduce_dimension)
            else:
                op = op.add_literal_column(
                    column_name=embedding_column_tmp_name,
                    literal=[],
                    dtype=pa.large_list(pa.float32()),
                    ftype=op_graph.feature_type.embedding(),
                )
            op = (
                op.and_then(select_columns)
                .and_then(update_feature_types)
                .and_then(rename_columns)
                .and_then(add_literal_column)
            )

            match op:
                case Ok(table):
                    pass
                case InvalidArgumentError() as err:
                    return err

            tables[output_source.name] = Table.from_ops(self.client, table)

        return Ok(tables)


class EmbedImageParameters:
    proto_self: Final[embedding_models_pb2.EmbedImageParameters]

    def __init__(self, proto_self: embedding_models_pb2.EmbedImageParameters):
        self.proto_self = proto_self

    @classmethod
    def create(
        cls, column_name: str, model_name: str, expected_vector_length: int
    ) -> Self:
        return cls(
            embedding_models_pb2.EmbedImageParameters(
                column_name=column_name,
                model_parameters=embedding_models_pb2.ImageModelParameters(
                    model=name_to_proto_image_model.get(
                        model_name,
                        embedding_models_pb2.IMAGE_MODEL_UNSPECIFIED,
                    ),
                    ndim=expected_vector_length,
                ),
            )
        )

    @property
    def column_name(self) -> str:
        return self.proto_self.column_name

    @property
    def model_name(self) -> str:
        return _image_model_proto_to_name_unsafe(self.proto_self.model_parameters.model)

    @property
    def model(self) -> embedding_models_pb2.ImageModel:
        return self.proto_self.model_parameters.model

    @property
    def expected_vector_length(self) -> int:
        return self.proto_self.model_parameters.ndim


class ImageSpace(Space):
    """Spaces for embedding images."""

    @property
    def parameters(self) -> EmbedImageParameters:
        return EmbedImageParameters(
            self.proto_self.space_parameters.embed_image_parameters
        )

    @property
    def output_source(self):
        return self.feature_view.output_sources[0]

    def _sub_orm_objects(self, orm_object: eorm.Space) -> Iterable[eorm.Base]:
        return []

    @property
    def expected_coordinate_bitwidth(self) -> Literal[32]:
        return 32

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: str,
        feature_view: FeatureView,
        parameters: EmbedImageParameters,
        room_id: eorm.RoomID,
        auto_sync: bool = False,
        client: system.Client,
    ) -> Ok[Self] | InvalidArgumentError:
        if len(feature_view.output_sources) != 1:
            return InvalidArgumentError(
                "feature view must have exactly one output source"
            )
        proto_self = models_pb2.Space(
            name=name,
            description=description,
            auto_sync=auto_sync,
            feature_view=feature_view.proto_self,
            room_id=str(room_id),
            space_parameters=space_pb2.SpaceParameters(
                embed_image_parameters=parameters.proto_self
            ),
        )
        return Ok(
            cls(
                proto_self=proto_self,
                client=client,
            )
        )

    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        params = self.parameters
        model_name = params.model_name
        output_source = self.output_source
        pk_field = output_source.table.schema.get_primary_key()
        if not pk_field:
            return InvalidArgumentError("output source must have a primary key")

        embedding_column_tmp_name = f"__embed-{uuid.uuid4()}"

        return (
            output_source.table.op_graph.embed_image_column(
                column_name=params.column_name,
                embedding_column_name=embedding_column_tmp_name,
                model_name=model_name,
                expected_vector_length=params.expected_vector_length,
                expected_coordinate_bitwidth=self.expected_coordinate_bitwidth,
            )
            .and_then(
                lambda t: t.select_columns([pk_field.name, embedding_column_tmp_name])
            )
            .and_then(
                lambda t: t.rename_columns(
                    {pk_field.name: "entity_id", embedding_column_tmp_name: "embedding"}
                )
            )
            .and_then(
                lambda t: t.add_literal_column(
                    "source_id",
                    str(output_source.id),
                    pa.string(),
                )
            )
            .map(lambda t: {output_source.name: Table.from_ops(self.client, t)})
        )


SpecificSpace: TypeAlias = (
    RelationalSpace | SemanticSpace | TabularSpace | ImageSpace | UnknownSpace
)

SpecificSpaceParameters: TypeAlias = (
    Node2VecParameters
    | ConcatAndEmbedParameters
    | EmbedAndConcatParameters
    | EmbedImageParameters
)
