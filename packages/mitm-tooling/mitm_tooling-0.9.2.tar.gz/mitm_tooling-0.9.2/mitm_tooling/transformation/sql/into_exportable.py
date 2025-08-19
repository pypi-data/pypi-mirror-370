from mitm_tooling.definition import ConceptName
from mitm_tooling.extraction.sql.data_models import TableMetaInfo, VirtualView
from mitm_tooling.extraction.sql.mapping import DataProvider, Exportable, HeaderEntryProvider, InstancesProvider
from mitm_tooling.extraction.sql.mapping.concept_mapping import ColumnContentProvider, InstancesPostProcessor
from mitm_tooling.representation.intermediate import Header
from mitm_tooling.representation.sql import SQLRepresentationSchema


def sql_rep_into_exportable(header: Header, sql_rep_schema: SQLRepresentationSchema) -> Exportable:
    """
    Create an `Exportable` from a `Header` by binding the concepts and types to the tables specified in the `SQLRepresentationSchema`.
    """

    data_providers: dict[ConceptName, list[DataProvider]] = {}
    for he in header.header_entries:
        if (type_t := sql_rep_schema.type_tables.get(he.concept, {}).get(he.type_name)) is not None:
            tm = TableMetaInfo.from_sa_table(type_t)
            typing_concept = header.mitm_def.get_properties(he.concept).typing_concept
            if he.concept not in data_providers:
                data_providers[he.concept] = []

            data_providers[he.concept].append(
                DataProvider(
                    instance_provider=InstancesProvider(
                        virtual_view=VirtualView(table_meta=tm, from_clause=type_t, sa_table=type_t)
                    ),
                    header_entry_provider=HeaderEntryProvider(
                        concept=he.concept,
                        table_meta=tm,
                        kind_provider=ColumnContentProvider.from_static('kind', he.kind),
                        type_provider=ColumnContentProvider.from_static(typing_concept, he.type_name),
                        attributes=list(he.attributes),
                        attribute_dtypes=list(he.attribute_dtypes),
                    ),
                    instance_postprocessor=InstancesPostProcessor(),
                )
            )

    return Exportable(mitm=header.mitm, data_providers=data_providers)
