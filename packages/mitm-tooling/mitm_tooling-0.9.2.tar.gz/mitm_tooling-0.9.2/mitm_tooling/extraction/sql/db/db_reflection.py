from collections.abc import Collection
from typing import Any

import pydantic
from sqlalchemy import Engine, MetaData, inspect

from mitm_tooling.representation.sql import SchemaName
from mitm_tooling.utilities.sql_utils import qualify

from ..data_models import TableMetaInfo


class TableDoesNotExist(Exception):
    pass


class AdditionalMeta(pydantic.BaseModel):
    default_schema: SchemaName


def connect_and_reflect(
    engine: Engine,
    meta: MetaData | None = None,
    allowed_schemas: Collection[str] | None = None,
    reflect_kwargs: dict[str, Any] | None = None,
) -> tuple[MetaData, AdditionalMeta]:
    inspector = inspect(engine)
    schemas = inspector.get_schema_names()

    kwargs = dict(resolve_fks=True, views=True, extend_existing=True, autoload_replace=True)
    if reflect_kwargs:
        kwargs |= reflect_kwargs

    meta = meta if meta else MetaData()
    if schemas:
        for schema in schemas:
            if not allowed_schemas or schema in allowed_schemas:
                meta.reflect(engine, schema=schema, **kwargs)
    else:
        meta.reflect(engine, **kwargs)

    return meta, AdditionalMeta(
        default_schema=(inspector.default_schema_name if inspector.default_schema_name else next(iter(meta._schemas)))
    )


def derive_table_meta_info(
    sa_meta: MetaData, name: str, schema: SchemaName | None = None, default_schema: SchemaName | None = None
) -> TableMetaInfo:
    qualified = qualify(table=name, schema=schema)
    try:
        t = sa_meta.tables[qualified]
        return TableMetaInfo.from_sa_table(t, default_schema=default_schema)
    except KeyError as e:
        raise TableDoesNotExist from e
