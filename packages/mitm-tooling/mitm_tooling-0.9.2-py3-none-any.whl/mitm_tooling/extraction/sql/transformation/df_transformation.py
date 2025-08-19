from abc import ABC, abstractmethod

import pandas as pd


class PandasSeriesTransform(ABC):
    @abstractmethod
    def transform_series(self, s: pd.Series) -> pd.Series:
        pass


class PandasCreation(ABC):
    @abstractmethod
    def make_series(self, df: pd.DataFrame) -> [pd.Series]:
        pass


class PandasDataframeTransform(ABC):
    @abstractmethod
    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


def extract_json_path(obj, path: tuple[str, ...]) -> dict | int | float | str | list | None:
    if not path:
        return obj
    elif isinstance(obj, dict):
        return extract_json_path(obj.get(path[0], None), path[1:])


def transform_df(df: pd.DataFrame, transforms: list[PandasDataframeTransform]) -> pd.DataFrame:
    for trans in transforms:
        df = trans.transform_df(df)
    return df
