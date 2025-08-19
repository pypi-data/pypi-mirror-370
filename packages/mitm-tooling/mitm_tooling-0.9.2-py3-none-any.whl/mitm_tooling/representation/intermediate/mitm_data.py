from collections import defaultdict
from collections.abc import Iterable
from typing import Self

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import get_mitm_def
from mitm_tooling.definition.definition_representation import ConceptName

from ..common import MITMTypeError
from ..intermediate.header import Header


class MITMData(Iterable[tuple[ConceptName, pd.DataFrame]], pydantic.BaseModel):
    """
    This model represents MITM data in a semi-compacted form; essentially the proposed csv file format.
    The individual DataFrames are expected to have fixed columns, corresponding to the type information in the `header`.
    In particular, each DataFrame should have the static columns as defined the `concept` it belongs to,
    and additionally a variable number of attribute columns named `a_1,a_2,...`.

    By default, it is assumed that the DataFrames are in the "generalized" form, meaning that the keys of the dictionary correspond to main concepts.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    concept_dfs: dict[ConceptName, pd.DataFrame] = pydantic.Field(default_factory=dict)

    def __iter__(self):
        return iter(self.concept_dfs.items())

    def as_generalized(self) -> Self:
        """
        Generalizes the MITMData by concatenating all DataFrames with the same _parent_ concept.
        For example, for a concept hierarchy like:

        - observation
            - measurement
            - event

        The DataFrames for `measurement` and `event` will be concatenated into the DataFrame for `observation`.
        """
        mitm_def = get_mitm_def(self.header.mitm)
        dfs = defaultdict(list)
        for c, df in self.concept_dfs.items():
            c_ = mitm_def.get_parent(c)
            if not c_:
                raise MITMTypeError(f'Encountered unknown concept key: "{c}".')
            dfs[c_].append(df)
        dfs = {c: pd.concat(dfs_, axis='index', ignore_index=True) for c, dfs_ in dfs.items()}
        return MITMData(header=self.header, concept_dfs=dfs)

    def as_specialized(self) -> Self:
        """
        Specializes the MITMData by splitting all DataFrames into their leaf concepts.
        For example, for a concept hierarchy like:

        - observation
            - measurement
            - event

        The DataFrame for `observation` will be split into `measurement` and `event`.
        """
        mitm_def = get_mitm_def(self.header.mitm)
        dfs = {}
        for c, df in self:
            if mitm_def.get_properties(c).is_abstract:
                # leaf_concepts = mitm_def.get_leafs(c)

                for sub_c_key, idx in df.groupby('kind').groups.items():
                    try:
                        sub_c = mitm_def.inverse_concept_key_map[str(sub_c_key)]
                    except KeyError:
                        raise MITMTypeError(f'Encountered unknown sub concept key: "{sub_c_key}".') from None
                    dfs[sub_c] = df.loc[idx]
            else:
                dfs[c] = df
        return MITMData(header=self.header, concept_dfs=dfs)
