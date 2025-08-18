# -*- coding: UTF-8 -*-
import abc
import dataclasses
import functools
import inspect
import typing

from dmasyncwrapper import Pool, consts

_NAMED_POOL_DICT: dict[str, Pool] = dict()


async def init(
        *, pool_name: str, host: str, port: int, user: str, password: str,
        auto_commit: bool,
        local_code: consts.LocalCode = consts.LocalCode.PG_UTF8,
        min_size: int, max_size: int,
) -> None:
    pool = Pool(
        host=host, port=port, user=user, password=password,
        auto_commit=auto_commit, local_code=local_code,
        min_size=min_size, max_size=max_size)
    await pool.init()
    _NAMED_POOL_DICT[pool_name] = pool


async def close(*, pool_name: str) -> None:
    if pool_name not in _NAMED_POOL_DICT:
        raise ValueError(f'Pool with name {pool_name} does not exist')
    pool = _NAMED_POOL_DICT[pool_name]
    await pool.close()
    del _NAMED_POOL_DICT[pool_name]


async def close_all() -> None:
    for _, pool in _NAMED_POOL_DICT.items():
        await pool.close()
    _NAMED_POOL_DICT.clear()


def with_dm(*, name: str, transaction: bool = True):

    def wrapper(func):
        argspec = inspect.getfullargspec(func)
        if all(map(lambda x: 'cursor' not in x,
                   (argspec.args, argspec.kwonlyargs))):
            raise SyntaxError('`cursor` is a required argument')

        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if name not in _NAMED_POOL_DICT:
                raise SyntaxError(f'Pool "{name}" not found')
            if 'cursor' in kwargs:
                raise SyntaxError('`cursor` is a reserved argument')
            async with _NAMED_POOL_DICT[name].acquire() as conn:
                await conn.ping(reconnect=True)
                async with conn.cursor() as cursor:
                    if transaction:
                        await cursor.execute('START TRANSACTION')
                    kwargs['cursor'] = cursor
                    try:
                        result = await func(*args, **kwargs)
                        await conn.commit()
                    except Exception as e:
                        await conn.rollback()
                        raise e
            return result

        return wrapped

    return wrapper


class SQLHelper:

    def __init__(self, base_model: type | None = None):
        try:
            assert dataclasses.is_dataclass(base_model) or base_model is None
        except AssertionError:
            raise SyntaxError(
                f'Base model "{base_model}" should be a dataclass or None')
        self._base_model = base_model

    def _gen_fields(self, dataclass: type) -> tuple[list[str], list[str]]:
        if self._base_model and issubclass(dataclass, self._base_model):
            default_fields = [
                i.strip('_')
                for i in inspect.get_annotations(self._base_model).keys()]
        else:
            default_fields = list()
        custom_fields = [
            i.strip('_') for i in inspect.get_annotations(dataclass).keys()]
        return default_fields, custom_fields

    def gen_select_base(
            self, *, dataclass: type, schema_name: str, table_name: str,
            quote_column: bool = True,
    ) -> str:
        default_fields, custom_fields = self._gen_fields(dataclass)
        fields_subquery_item = [
            (f'"{item}"' if quote_column else item)
            for item in (default_fields + custom_fields)]
        return (f'SELECT {", ".join(fields_subquery_item)} '
                f'FROM "{schema_name}"."{table_name}"')

    def gen_insert(
            self, *, dataclass: type, schema_name: str, table_name: str,
            quote_column: bool = True,
    ) -> str:
        _, custom_fields = self._gen_fields(dataclass)
        insert_subquery = ', '.join(
            f'"{item}"' if quote_column else item for item in custom_fields)
        return (f'INSERT INTO "{schema_name}"."{table_name}" '
                f'({insert_subquery}) '
                f'VALUES ({", ".join(["?"] * len(custom_fields))})')

    def gen_insert_returning(
            self, *, dataclass: type, schema_name: str, table_name: str,
    ) -> str:
        default_fields, custom_fields = self._gen_fields(dataclass)
        return (f'INSERT INTO "{schema_name}"."{table_name}" '
                f'({", ".join(custom_fields)}) '
                f'VALUES ({", ".join(["?"] * len(custom_fields))}) '
                f'RETURNING {", ".join(default_fields + custom_fields)}')

    def gen_upsert(
            self, *, dataclass: type, schema_name: str, table_name: str,
            unique_key_columns: typing.Sequence[str],
            quote_column: bool = True,
    ) -> str:
        _, custom_fields = self._gen_fields(dataclass)
        if set(unique_key_columns) == set(custom_fields):
            ignore_info = f'"{table_name}" ({", ".join(unique_key_columns)})'
            place_holder = ', '.join(['?'] * len(custom_fields))
            sql = f"""
INSERT /*+ IGNORE_ROW_ON_DUPKEY_INDEX({ignore_info}) */
INTO "{schema_name}"."{table_name}" ({", ".join(custom_fields)})
VALUES ({place_holder});
"""
        else:
            select_subquery = ', '.join(
                f'? AS {field}' for field in custom_fields)
            on_sub_query = ' AND '.join(
                f'S."{col}" = D.{col}'
                if quote_column else f'S.{col} = D.{col}'
                for col in unique_key_columns)
            update_set_subquery = ', '.join(
                f'S."{field}" = D.{field}'
                if quote_column else f'S.{field} = D.{field}'
                for field in custom_fields
                if field not in unique_key_columns)
            insert_subquery = ', '.join(
                f'"{item}"' if quote_column else item
                for item in custom_fields)
            values_subquery = ', '.join(
                'D.' + field for field in custom_fields)
            sql = f"""
MERGE INTO "{schema_name}"."{table_name}" AS S
USING (SELECT {select_subquery} FROM DUAL) AS D
ON ({on_sub_query})
WHEN MATCHED THEN UPDATE SET {update_set_subquery}
WHEN NOT MATCHED THEN INSERT ({insert_subquery}) VALUES ({values_subquery})
"""
        return sql.strip().replace('\n', ' ')


@dataclasses.dataclass(slots=True, kw_only=True)
class BaseInsertModel(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def as_sql_params(self) -> tuple:
        ...
