from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import ConceptName, TypeName

from ..intermediate.header import Header
from .common import MITMDataFrameStream, TypedMITMDataFrameStream

if TYPE_CHECKING:
    from .streaming_mitm_dataframes import StreamingMITMDataFrames


class MITMDataFrames(Iterable[tuple[ConceptName, dict[TypeName, pd.DataFrame]]], pydantic.BaseModel):
    """
    This model represents normalized MITM Data as a collection of pandas DataFrames, hierarchically organized by concept and type.
    It is intended to be used for in-memory representation of normalized MITM Data, e.g., when feeding it into data science packages.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    dfs: dict[ConceptName, dict[TypeName, pd.DataFrame]]

    def __iter__(self):
        return iter(self.dfs.items())

    def stream(self) -> MITMDataFrameStream:
        return ((c, ((t, (df,)) for t, df in dfs.items())) for c, dfs in self.dfs.items())

    def typed_stream(self) -> TypedMITMDataFrameStream:
        he_dict = self.header.as_dict
        return ((c, ((t, he_dict[c][t], (df,)) for t, df in dfs.items())) for c, dfs in self.dfs.items())

    def as_streaming(self) -> StreamingMITMDataFrames:
        from .streaming_mitm_dataframes import StreamingMITMDataFrames

        return StreamingMITMDataFrames(
            header=self.header, df_iters={c: {t: (df,) for t, df in dfs.items()} for c, dfs in self.dfs.items()}
        )
