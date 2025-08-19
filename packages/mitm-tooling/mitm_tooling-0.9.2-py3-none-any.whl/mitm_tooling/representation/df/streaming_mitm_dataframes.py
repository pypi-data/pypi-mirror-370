from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import ConceptName, TypeName

from ..intermediate.header import Header
from .common import MITMDataFrameStream, TypedMITMDataFrameStream


class StreamingMITMDataFrames(Iterable[tuple[ConceptName, dict[TypeName, pd.DataFrame]]], pydantic.BaseModel):
    """
    This model explicitly represents a stream of structured MITM Data via a collection of Iterables.
    In contrast to the bare `MITMDataFrameStream`, only the instances are (potentially) streamed, not the type information.

    Note: Streamed data is assumed to be readable once.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    df_iters: dict[ConceptName, dict[TypeName, Iterable[pd.DataFrame]]]

    def __iter__(self):
        return iter(self.df_iters.items())

    def stream(self) -> MITMDataFrameStream:
        return ((c, ((t, df_iter) for t, df_iter in dfs.items())) for c, dfs in self.df_iters.items())

    def typed_stream(self) -> TypedMITMDataFrameStream:
        he_dict = self.header.as_dict
        return ((c, ((t, he_dict[c][t], df_iter) for t, df_iter in dfs.items())) for c, dfs in self.df_iters.items())
