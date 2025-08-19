from collections.abc import Mapping

import pandas as pd

from mitm_tooling.data_types import MITMDataType, convert
from mitm_tooling.definition import ConceptName, TypeName
from mitm_tooling.representation import mk_concept_file_header
from mitm_tooling.representation.common import MITMTypeError
from mitm_tooling.representation.df import MITMDataFrames
from mitm_tooling.representation.intermediate import Header, MITMData
from mitm_tooling.representation.intermediate.header import mk_type_table_columns


def pack_typed_dfs_as_concept_table(
    header: Header, concept: ConceptName, dfs: Mapping[TypeName, pd.DataFrame]
) -> pd.DataFrame:
    """
    Pack multiple typed data frames into a single concept table.
    They are expected to have columns in the format of `MITMDataFrames`, i.e.,
    they at least contain the base columns determined by the concept in the specified MITM.
    The resulting data frame has the structure of `MITMData`.

    :param header: a header which contains `HeaderEntries` for each of the occurring types
    :param concept: the target concept
    :param dfs: mapping of individual types to data frames belonging to the target concept
    :return: a single concatenated data frame
    """
    props = header.mitm_def.get_properties(concept)
    if props is None:
        raise MITMTypeError(f'Concept {concept} missing in header.')
    normalized_dfs: list[tuple[pd.DataFrame, int]] = []
    for type_name, df in dfs.items():
        if props.typing_concept not in df.columns:
            df[props.typing_concept] = type_name

        if 'kind' not in df.columns:
            df['kind'] = props.key
        else:
            df.loc[df['kind'].isna(), 'kind'] = props.key
        # alternatively, something like:
        # df = df.assign(kind=lambda x: x['kind'].fillna(props.key) if 'kind' in x.columns else props.key)

        he = header.get(concept, type_name)
        if he is None:
            raise MITMTypeError(f'Missing type entry for {concept}:{type_name} in header.')
        normal_form_cols, col_dts = mk_type_table_columns(header.mitm, he)

        df = df.reindex(columns=normal_form_cols)

        df = convert.convert_df(df, col_dts | {c: MITMDataType.Unknown for c in he.attributes})
        squashed_form_cols = mk_concept_file_header(header.mitm, concept, he.attr_k)[0]
        df.columns = squashed_form_cols
        normalized_dfs.append((df, he.attr_k))

    max_k = max(normalized_dfs, key=lambda x: x[1])[1] if normalized_dfs else 0

    squashed_form_cols = mk_concept_file_header(header.mitm, concept, max_k)[0]
    if len(normalized_dfs) > 0:
        return pd.concat([df for df, _ in normalized_dfs], axis='index', ignore_index=True).reindex(
            columns=squashed_form_cols
        )
    else:
        return pd.DataFrame(columns=squashed_form_cols)


def mitm_dataframes_into_mitm_data(mitm_dataset: MITMDataFrames) -> MITMData:
    """
    Convert a `MITMDataFrames` object into a `MITMData` object.
    """
    return MITMData(
        header=mitm_dataset.header,
        concept_dfs={
            concept: pack_typed_dfs_as_concept_table(mitm_dataset.header, concept, typed_dfs)
            for concept, typed_dfs in mitm_dataset
            if len(typed_dfs) > 0
        },
    ).as_generalized()
