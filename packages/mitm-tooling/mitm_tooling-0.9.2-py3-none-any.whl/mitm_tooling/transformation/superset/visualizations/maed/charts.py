from collections.abc import Sequence

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.definition import MITM, ConceptName, RelationName, TypeName, get_mitm_def
from mitm_tooling.representation.intermediate import Header, HeaderEntry
from mitm_tooling.representation.sql import SQLRepresentationSchema, TableName, mk_sql_rep_schema
from mitm_tooling.utilities.identifiers import naive_pluralize

from ...asset_bundles import NamedChartIdentifierMap
from ...definitions import (
    ChartIdentifier,
    ChartIdentifierMap,
    DatasetIdentifier,
    DatasetIdentifierMap,
    FilterOperator,
    MitMDatasetIdentifier,
    SupersetAggregate,
    SupersetChartDef,
)
from ...factories.core import mk_adhoc_filter, mk_adhoc_metric, mk_adhoc_metrics, mk_metric
from ...factories.custom_charts import mk_maed_custom_chart
from ...factories.generic_charts import (
    mk_agg_table_chart,
    mk_avg_count_time_series_chart,
    mk_big_number_chart,
    mk_horizon_chart,
    mk_metric_time_series_chart,
    mk_pie_chart,
    mk_raw_table_chart,
    mk_time_series_bar_chart,
)
from ..abstract import ChartCollectionCreator, ChartCreator, ChartDefCollection


class ConceptCountTS(ChartCreator):
    def __init__(
        self,
        concept: ConceptName,
        groupby_relations: Sequence[RelationName] = ('object',),
        time_relation: RelationName = 'time',
    ):
        self.concept = concept
        self.groupby_relations = list(groupby_relations)
        self.time_relation = time_relation
        props, rels = get_mitm_def(MITM.MAED).get(concept)
        self.props = props
        self.relations = rels
        defined_relations = set(self.relations.relation_names)
        assert set(self.groupby_relations) <= defined_relations
        assert self.time_relation in self.relations.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.concept.title()} Counts'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        filters = [mk_adhoc_filter('kind', FilterOperator.EQUALS, self.props.key)] if self.props.is_sub else None
        return mk_time_series_bar_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            self.props.typing_concept,
            MITMDataType.Text,
            x_col=self.time_relation,
            groupby_cols=self.groupby_relations,
            filters=filters,
            uuid=chart_identifier.uuid,
        )


class RelationPie(ChartCreator):
    def __init__(self, concept: ConceptName, relation: RelationName):
        self.relation = relation
        assert relation in get_mitm_def(MITM.MAED).get_relations(concept).relation_names

    @property
    def slice_name(self) -> str:
        return naive_pluralize(self.relation).title()

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_pie_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            col=self.relation,
            dt=MITMDataType.Text,
            groupby_cols=[self.relation],
            uuid=chart_identifier.uuid,
        )


class TypeCountBigNumber(ChartCreator):
    def __init__(self, concept: ConceptName, type_name: TypeName, time_relation: RelationName | None = 'time'):
        self.type_name = type_name
        self.time_relation = time_relation
        props, rels = get_mitm_def(MITM.MAED).get(concept)
        self.props = props
        if self.time_relation:
            assert self.time_relation in rels.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.type_name.title()} Big Number'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_big_number_chart(
            chart_identifier.slice_name,
            mk_adhoc_metric(self.props.typing_concept, SupersetAggregate.COUNT),
            dataset_identifier,
            agg='sum',
            time_col=self.time_relation,
            uuid=chart_identifier.uuid,
        )


class TypeCountsHorizon(ChartCreator):
    def __init__(
        self,
        concept: ConceptName,
        time_relation: RelationName | None = 'time',
        additional_groupby_relations: Sequence[RelationName] = ('object',),
    ):
        self.concept = concept
        self.time_relation = time_relation
        self.additional_groupby_relations = additional_groupby_relations
        props, rels = get_mitm_def(MITM.MAED).get(concept)
        self.props = props
        if self.time_relation:
            assert self.time_relation in rels.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.concept.title()} Horizon'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        # I am counting on the fact that every programmatically created dataset has a COUNT(*) metric
        # alternatively, use mk_adhoc_metric(self.props.typing_concept, SupersetAggregate.COUNT)
        count_metric = mk_metric('*', SupersetAggregate.COUNT).metric_name
        groupby = [self.props.typing_concept]
        if self.additional_groupby_relations:
            groupby.extend(self.additional_groupby_relations)
        return mk_horizon_chart(
            chart_identifier.slice_name,
            [count_metric],
            dataset_identifier,
            groupby_cols=groupby,
            time_col=self.time_relation,
        )


class NumericAttributesTS(ChartCreator):
    def __init__(
        self,
        header_entry: HeaderEntry,
        groupby_relations: Sequence[RelationName] = ('object',),
        time_relation: RelationName = 'time',
    ):
        self.header_entry = header_entry
        self.groupby_relations = list(groupby_relations)
        self.time_relation = time_relation
        props, rels = get_mitm_def(MITM.MAED).get(header_entry.concept)
        self.props = props
        self.relations = rels
        defined_relations = set(self.relations.relation_names)
        assert set(self.groupby_relations) <= defined_relations
        assert self.time_relation in self.relations.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.header_entry.type_name.title()} Time Series'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_metric_time_series_chart(
            chart_identifier.slice_name,
            mk_adhoc_metrics(
                [
                    a
                    for a, dt in zip(self.header_entry.attributes, self.header_entry.attribute_dtypes, strict=False)
                    if dt == MITMDataType.Numeric
                ]
            ),
            dataset_identifier,
            groupby_cols=self.groupby_relations,
            time_col=self.time_relation,
            uuid=chart_identifier.uuid,
        )


class ConceptTypeAvgCountTS(ChartCreator):
    def __init__(
        self,
        concept: ConceptName,
        type_name: TypeName,
        groupby_relations: Sequence[RelationName] = ('object',),
        time_relation: RelationName = 'time',
    ):
        self.concept = concept
        self.type_name = type_name
        self.groupby_relations = list(groupby_relations)
        self.time_relation = time_relation
        props, rels = get_mitm_def(MITM.MAED).get(concept)
        self.props = props
        self.relations = rels
        defined_relations = set(self.relations.relation_names)
        assert set(self.groupby_relations) <= defined_relations
        assert self.time_relation in self.relations.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.type_name.title()} Count Time Series'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_avg_count_time_series_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            groupby_cols=self.groupby_relations,
            time_col=self.time_relation,
            uuid=chart_identifier.uuid,
        )


class TypeCountsTableChart(ChartCreator):
    @property
    def slice_name(self) -> str:
        return 'Header Type Counts'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_agg_table_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            metrics=[mk_adhoc_metric('type', SupersetAggregate.COUNT)],
            groupby=['kind', 'concept'],
            uuid=chart_identifier.uuid,
        )


class TypesTableChart(ChartCreator):
    @property
    def slice_name(self) -> str:
        return 'Header Types'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_raw_table_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            ['kind', 'concept', 'type'],
            orderby=[('kind', True), ('type', True)],
            uuid=chart_identifier.uuid,
        )


class ConceptTypesTableChart(ChartCreator):
    def __init__(self, concept: ConceptName):
        self.concept = concept
        self.props = get_mitm_def(MITM.MAED).get_properties(concept)

    @property
    def slice_name(self) -> str:
        return f'{self.concept.title()} Types'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_raw_table_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            ['type', 'attribute_name'],
            filters=[mk_adhoc_filter('kind', FilterOperator.EQUALS, self.props.key)],
            orderby=[('type', True)],
            uuid=chart_identifier.uuid,
        )


class TypeAttributesTableChart(ChartCreator):
    def __init__(self, concept: ConceptName, type_name: TypeName):
        self.concept = concept
        self.type_name = type_name
        self.props = get_mitm_def(MITM.MAED).get_properties(concept)

    @property
    def slice_name(self) -> str:
        return f'{self.type_name.title()} Attributes'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_raw_table_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            ['attribute_name', 'attribute_dtype'],
            filters=[
                mk_adhoc_filter('kind', FilterOperator.EQUALS, self.props.key),
                mk_adhoc_filter('type', FilterOperator.EQUALS, self.type_name),
            ],
            orderby=[('attribute_order', True)],
            uuid=chart_identifier.uuid,
        )


class ConceptTypesAvgCountTSCollection(ChartCollectionCreator):
    def __init__(self, concept: ConceptName, sql_rep_schema: SQLRepresentationSchema):
        super().__init__()
        self.sql_rep_schema = sql_rep_schema
        self.concept = concept

    @property
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
        ccs = {}
        for type_name, tbl in self.sql_rep_schema.type_tables.get(self.concept, {}).items():
            ccs[f'{self.concept}-{type_name}-count-ts'] = (tbl.name, ConceptTypeAvgCountTS(self.concept, type_name))
        return ccs


class AverageAttributesTSCollection(ChartCollectionCreator):
    def __init__(self, concept: ConceptName, header: Header, sql_rep_schema: SQLRepresentationSchema):
        super().__init__()
        self.concept = concept
        self.header = header
        self.sql_rep_schema = sql_rep_schema
        assert all(
            t in self.header.as_dict[self.concept] for t in self.sql_rep_schema.type_tables.get(self.concept, {}).keys()
        )

    @property
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
        ccs = {}
        for type_name, tbl in self.sql_rep_schema.type_tables.get(self.concept, {}).items():
            he = self.header.as_dict[self.concept][type_name]
            ccs[f'{self.concept}-{type_name}-ts'] = (tbl.name, (NumericAttributesTS(he)))
        return ccs


class BigNumberCollection(ChartCollectionCreator):
    def __init__(self, concepts: Sequence[ConceptName], sql_rep_schema: SQLRepresentationSchema):
        self.concepts = concepts
        self.sql_rep_schema = sql_rep_schema

    @property
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
        return {
            f'{c}-{type_name}-big-number': (tbl.name, TypeCountBigNumber(c, type_name))
            for c in self.concepts
            for type_name, tbl in self.sql_rep_schema.type_tables.get(c, {}).items()
        }


class HeaderMetaTables(ChartCollectionCreator):
    def __init__(self, header: Header, sql_rep_schema: SQLRepresentationSchema):
        super().__init__()
        self.header = header
        self.sql_rep_schema = sql_rep_schema
        assert self.sql_rep_schema.meta_tables.type_attributes is not None

    @property
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
        tbl_name = self.sql_rep_schema.meta_tables.type_attributes.name
        ccs = {}
        ccs['header-types-table'] = (self.sql_rep_schema.meta_tables.types.name, TypesTableChart())
        ccs['header-counts-table'] = (self.sql_rep_schema.meta_tables.types.name, TypeCountsTableChart())
        for c, type_map in self.header.as_dict.items():
            # ccs[f'{c}-types-table'] = (tbl_name, ConceptTypesTableChart(c))
            for type_name, _he in type_map.items():
                ccs[f'{c}-{type_name}-attributes-table'] = (tbl_name, TypeAttributesTableChart(c, type_name))
        return ccs


class BaselineMAEDCharts(ChartCollectionCreator):
    def __init__(self, header: Header, sql_rep_schema: SQLRepresentationSchema | None = None):
        super().__init__()
        self.header = header
        self.sql_rep_schema = sql_rep_schema or mk_sql_rep_schema(header)
        self.mitm_def = header.mitm_def

    @property
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
        ccs = {}
        observation_table_name = self.sql_rep_schema.concept_tables['observation'].name
        for sub_concept in self.mitm_def.sub_concept_map['observation']:
            ccs[f'{sub_concept}-count-ts'] = (observation_table_name, ConceptCountTS(sub_concept))
        ccs['observation-objects-pie'] = (observation_table_name, RelationPie('observation', 'object'))
        ccs['event-horizon'] = (self.sql_rep_schema.view_tables['events_view'].name, TypeCountsHorizon('event'))
        return ccs

    def mk_chart_collection(self, ds_id_map: DatasetIdentifierMap, ch_id_map: ChartIdentifierMap) -> ChartDefCollection:
        charts = super().mk_chart_collection(ds_id_map, ch_id_map)
        charts.update(
            BigNumberCollection(['event', 'measurement'], self.sql_rep_schema).mk_chart_collection(ds_id_map, ch_id_map)
        )

        charts.update(
            ConceptTypesAvgCountTSCollection('event', self.sql_rep_schema).mk_chart_collection(ds_id_map, ch_id_map)
        )
        charts.update(
            AverageAttributesTSCollection('measurement', self.header, self.sql_rep_schema).mk_chart_collection(
                ds_id_map, ch_id_map
            )
        )
        return charts


class ExperimentalMAEDCharts(ChartCollectionCreator):
    def __init__(self, header: Header, sql_rep_schema: SQLRepresentationSchema | None = None):
        super().__init__()
        self.header = header
        self.sql_rep_schema = sql_rep_schema or mk_sql_rep_schema(header)
        self.mitm_def = header.mitm_def

    @property
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
        return {}

    def mk_chart_collection(
        self, ds_id_map: DatasetIdentifierMap, ch_id_map: NamedChartIdentifierMap
    ) -> ChartDefCollection:
        return ChartCollectionCreator.union(HeaderMetaTables(self.header, self.sql_rep_schema)).mk_chart_collection(
            ds_id_map, ch_id_map
        )


class MAEDCustomChart(ChartCreator):
    def __init__(self, mdi: MitMDatasetIdentifier):
        self.mdi = mdi

    @property
    def slice_name(self) -> str:
        return 'Custom MAED Chart'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_maed_custom_chart(
            chart_identifier.slice_name, self.mdi, dataset_identifier, uuid=chart_identifier.uuid
        )
