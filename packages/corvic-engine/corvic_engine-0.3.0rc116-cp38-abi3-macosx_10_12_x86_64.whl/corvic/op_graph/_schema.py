"""Corvic feature schemas."""

from __future__ import annotations

from typing import cast

import polars as pl
import pyarrow as pa

import corvic.op_graph.feature_types as feature_type
from corvic import eorm
from corvic.op_graph.feature_types import FeatureType


def _infer_possible_feature_types(
    data_type: pa.DataType,
) -> list[FeatureType]:
    if pa.types.is_integer(data_type):
        # TODO(thunt): Add multi-categorical in future versions
        return [
            feature_type.numerical(),
            feature_type.identifier(),
            feature_type.primary_key(),
            feature_type.categorical(),
            feature_type.foreign_key(referenced_source_id=eorm.SourceID()),
            feature_type.unknown(),
        ]
    if pa.types.is_decimal(data_type) | pa.types.is_floating(data_type):
        return [
            feature_type.numerical(),
            feature_type.categorical(),
            feature_type.unknown(),
        ]
    if (
        pa.types.is_string(data_type)
        | pa.types.is_large_string(data_type)
        | pa.types.is_binary(data_type)
        | pa.types.is_large_binary(data_type)
    ):
        # TODO(thunt): Add multi-categorical in future versions
        return [
            feature_type.text(),
            feature_type.identifier(),
            feature_type.primary_key(),
            feature_type.categorical(),
            feature_type.foreign_key(referenced_source_id=eorm.SourceID()),
            feature_type.image(),
            feature_type.unknown(),
        ]
    if pa.types.is_boolean(data_type):
        # TODO(thunt): Add Numerical in future versions
        return [feature_type.categorical(), feature_type.unknown()]
    if (
        pa.types.is_list(data_type)
        | pa.types.is_fixed_size_list(data_type)
        | pa.types.is_large_list(data_type)
    ):
        return [feature_type.embedding(), feature_type.unknown()]
    if pa.types.is_temporal(data_type):
        # TODO(thunt): Add Identifier, Primary Key, Foreign Key, Categorical in future
        # versions
        return [feature_type.timestamp(), feature_type.unknown()]
    return [feature_type.unknown()]


def _upgrade_to_polars_dtype(dtype: pa.DataType) -> pa.DataType:
    if pa.types.is_string(dtype):
        return pa.large_string()
    if pa.types.is_binary(dtype):
        return pa.large_binary()
    if pa.types.is_float16(dtype):
        # polars does not support float16 unless explicitly enabled
        return pa.float32()
    if isinstance(dtype, pa.ListType | pa.LargeListType | pa.FixedSizeListType):
        dtype = cast(
            "pa.ListType[pa.DataType] | pa.LargeListType[pa.DataType] \
                | pa.FixedSizeListType[pa.DataType]",
            dtype,
        )
        # modify large lists as well since its value datatype
        # may need to be updated
        return pa.large_list(
            dtype.value_field.with_type(
                _upgrade_to_polars_dtype(dtype.value_field.type)
            )
        )
    if isinstance(dtype, pa.StructType):
        upgraded_nested_fields: list[pa.Field] = []
        for field_index in range(dtype.num_fields):
            nested_field = dtype.field(field_index)
            upgraded_nested_fields.append(
                nested_field.with_type(_upgrade_to_polars_dtype(nested_field.type))
            )
        return pa.struct(upgraded_nested_fields)
    return dtype


class Field:
    """A named field, with a data type and feature type."""

    _name: str
    _dtype: pa.DataType
    _ftype: FeatureType

    def __init__(
        self,
        name: str,
        dtype: pa.DataType,
        ftype: FeatureType,
    ) -> None:
        self._name = name
        self._dtype = _upgrade_to_polars_dtype(dtype)
        self._ftype = ftype

    def __str__(self) -> str:
        """Legible string representation."""
        return f"{self._name}: {self._dtype}, {self._ftype}"

    def __eq__(self, other: object) -> bool:
        """Two fields are equal if their contents match."""
        if isinstance(other, Field):
            return (
                self._name == other._name
                and self._dtype == other._dtype
                and self._ftype == other._ftype
            )
        return False

    @property
    def dtype(self) -> pa.DataType:
        return self._dtype

    @property
    def name(self) -> str:
        return self._name

    @property
    def ftype(self) -> FeatureType:
        return self._ftype

    @classmethod
    def decode_feature_type(cls, arrow_type: pa.DataType) -> FeatureType:
        ftypes = _infer_possible_feature_types(arrow_type)
        if not ftypes:
            raise ValueError("No feature types detected.")
        return ftypes[0]

    @classmethod
    def from_arrow(
        cls,
        arrow_field: pa.Field,
        feature_type: FeatureType | None = None,
    ) -> Field:
        feature_type = feature_type or cls.decode_feature_type(arrow_field.type)
        return Field(
            arrow_field.name,
            arrow_field.type,
            feature_type,
        )

    def to_arrow(self) -> pa.Field:
        return pa.field(
            self.name,
            self.dtype,
        )

    def to_polars(self) -> pl.DataType:
        table = pl.from_arrow(pa.schema([self.to_arrow()]).empty_table())
        if isinstance(table, pl.Series):
            table = table.to_frame()
        return table.schema[self.name]

    def rename(self, new_name: str) -> Field:
        return Field(new_name, self.dtype, self.ftype)

    def possible_feature_types(self) -> list[FeatureType]:
        """Infer possible feature types given the data type."""
        return _infer_possible_feature_types(self.dtype)
