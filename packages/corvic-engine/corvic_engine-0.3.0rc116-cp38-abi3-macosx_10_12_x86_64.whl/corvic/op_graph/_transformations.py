from typing import Literal, cast

import corvic.op_graph.ops as op
from corvic.result import InvalidArgumentError, Ok


def _replace_join_op_source(
    join_op: op.Join, source_to_replace: op.Op, new_source: op.Op
):
    if source_to_replace is join_op.left_source:
        return new_source.join(
            join_op.right_source,
            join_op.left_join_columns,
            join_op.right_join_columns,
            how=join_op.how,
        )

    if source_to_replace is join_op.right_source:
        return join_op.left_source.join(
            new_source,
            join_op.left_join_columns,
            join_op.right_join_columns,
            how=join_op.how,
        )

    return InvalidArgumentError("source_to_replace is not one of the join sources")


def _replace_rollup_by_aggregation_op_source(
    rollup_op: op.RollupByAggregation, source_to_replace: op.Op, new_source: op.Op
):
    return new_source.rollup_by_aggregation(
        group_by=rollup_op.group_by_column_names,
        target=rollup_op.target_column_name,
        aggregation=rollup_op.aggregation_type,
    )


def _replace_embed_node2vec_from_edge_lists_op(
    node2vec_op: op.EmbedNode2vecFromEdgeLists,
    source_to_replace: op.Op,
    new_source: op.Op,
):
    new_edge_list_tables = list[op.EdgeListTable]()
    for elt in node2vec_op.edge_list_tables:
        if elt.table is source_to_replace:
            new_edge_list_tables.append(
                op.EdgeListTable(
                    new_source,
                    start_column_name=elt.start_column_name,
                    end_column_name=elt.end_column_name,
                    start_entity_name=elt.start_entity_name,
                    end_entity_name=elt.end_entity_name,
                )
            )
        else:
            new_edge_list_tables.append(elt)
    return op.embed_node2vec_from_edge_lists(
        new_edge_list_tables,
        node2vec_op.to_proto().embed_node2vec_from_edge_lists.node2vec_parameters,
    )


def _replace_concat_op_source(
    concat_op: op.Concat, source_to_replace: op.Op, new_source: op.Op
):
    new_tables = list[op.Op]()
    for table in concat_op.tables:
        if table is source_to_replace:
            new_tables.append(new_source)
        else:
            new_tables.append(table)
    return op.concat(new_tables, concat_op.how)


def replace_op_source(  # noqa: C901, PLR0915
    root_op: op.Op, source_to_replace: op.Op, new_source: op.Op
) -> Ok[op.Op] | InvalidArgumentError:
    for source in root_op.sources():
        if source is source_to_replace:
            break
    else:
        return InvalidArgumentError("source_to_replace is not one of root_op's sources")

    match root_op:
        case (
            op.SelectFromStaging()
            | op.Empty()
            | op.SelectFromVectorStaging()
            | op.ReadFromParquet()
            | op.InMemoryInput()
        ):
            return InvalidArgumentError("root_op does not have a source to replace")
        case op.RenameColumns():
            return new_source.rename_columns(root_op.old_name_to_new)
        case op.Join():
            return _replace_join_op_source(root_op, source_to_replace, new_source)
        case op.SelectColumns():
            return new_source.select_columns(root_op.columns)
        case op.LimitRows():
            return new_source.limit_rows(root_op.num_rows)
        case op.OffsetRows():
            return new_source.offset_rows(root_op.num_rows)
        case op.OrderBy():
            return new_source.order_by(root_op.columns, desc=root_op.desc)
        case op.FilterRows():
            return new_source.filter_rows(row_filter=root_op.row_filter)
        case op.DistinctRows():
            return new_source.distinct_rows()
        case op.UpdateMetadata():
            return new_source.update_metadata(root_op.metadata_updates)
        case op.SetMetadata():
            return new_source.set_metadata(root_op.new_metadata)
        case op.RemoveFromMetadata():
            return new_source.remove_from_metadata(root_op.keys_to_remove)
        case op.UpdateFeatureTypes():
            return new_source.update_feature_types(root_op.new_feature_types)
        case op.RollupByAggregation():
            return _replace_rollup_by_aggregation_op_source(
                root_op, source_to_replace, new_source
            )
        case op.EmbedNode2vecFromEdgeLists():
            return _replace_embed_node2vec_from_edge_lists_op(
                root_op, source_to_replace, new_source
            )
        case op.EmbeddingMetrics():
            return op.quality_metrics_from_embedding(
                new_source, root_op.embedding_column_name
            )
        case op.EmbeddingCoordinates():
            return op.coordinates_from_embedding(
                new_source,
                root_op.embedding_column_name,
                root_op.n_components,
                cast(Literal["cosine", "euclidean"], root_op.metric),
            )
        case op.Concat():
            return _replace_concat_op_source(root_op, source_to_replace, new_source)
        case op.UnnestStruct():
            return new_source.unnest_struct(root_op.struct_column_name)
        case op.NestIntoStruct():
            return new_source.nest_into_struct(
                root_op.struct_column_name, root_op.column_names_to_nest
            )
        case op.AddLiteralColumn():
            new_proto = root_op.to_proto()
            new_proto.add_literal_column.source.CopyFrom(new_source.to_proto())
            return Ok(op.from_proto(new_proto, skip_validate=True))
        case op.CombineColumns():
            new_proto = root_op.to_proto()
            new_proto.combine_columns.source.CopyFrom(new_source.to_proto())
            return Ok(op.from_proto(new_proto, skip_validate=True))
        case op.EmbedColumn():
            return new_source.embed_column(
                column_name=root_op.column_name,
                embedding_column_name=root_op.embedding_column_name,
                model_name=root_op.model_name,
                tokenizer_name=root_op.tokenizer_name,
                expected_vector_length=root_op.expected_vector_length,
                expected_coordinate_bitwidth=root_op.expected_coordinate_bitwidth,
            )
        case op.EncodeColumns():
            return new_source.encode_columns(root_op.encoded_columns)
        case op.AggregateColumns():
            return new_source.aggregate_columns(
                root_op.column_names, root_op.aggregation
            )
        case op.CorrelateColumns():
            return new_source.correlate_columns(root_op.column_names)
        case op.HistogramColumn():
            return new_source.histogram(
                root_op.column_name,
                breakpoint_column_name=root_op.breakpoint_column_name,
                count_column_name=root_op.count_column_name,
            )
        case op.ConvertColumnToString():
            return new_source.convert_column_to_string(root_op.column_name)
        case op.AddRowIndex():
            return new_source.add_row_index(
                root_op.row_index_column_name, offset=root_op.offset
            )
        case op.OutputCsv():
            return new_source.output_csv(
                url=root_op.csv_url, include_header=root_op.include_header
            )
        case op.TruncateList():
            new_proto = root_op.to_proto()
            new_proto.truncate_list.source.CopyFrom(new_source.to_proto())
            return Ok(op.from_proto(new_proto, skip_validate=True))
        case op.Union():
            new_tables = list[op.Op]()
            for table in root_op.sources():
                if table is source_to_replace:
                    new_tables.append(new_source)
                else:
                    new_tables.append(table)
            return op.union(new_tables, distinct=root_op.distinct)
        case op.EmbedImageColumn():
            return new_source.embed_image_column(
                column_name=root_op.column_name,
                embedding_column_name=root_op.embedding_column_name,
                model_name=root_op.model_name,
                expected_vector_length=root_op.expected_vector_length,
                expected_coordinate_bitwidth=root_op.expected_coordinate_bitwidth,
            )
        case op.AddDecisionTreeSummary():
            return new_source.add_decision_tree_summary(
                feature_column_names=root_op.feature_column_names,
                label_column_name=root_op.label_column_name,
                max_depth=root_op.max_depth,
                output_metric_key=root_op.output_metric_key,
                classes_names=root_op.classes_names,
            )
        case op.UnnestList():
            return new_source.unnest_list(
                list_column_name=root_op.list_column_name,
                new_column_names=root_op.column_names,
            )
        case op.SampleRows():
            return new_source.sample_rows(
                sample_strategy=root_op.sample_strategy, num_rows=root_op.num_rows
            )
        case op.DescribeColumns():
            return new_source.describe(
                column_names=root_op.column_names,
                interpolation=root_op.interpolation,
                statistic_column_name=root_op.statistic_column_name,
            )
    return InvalidArgumentError("could not identify root_op")
