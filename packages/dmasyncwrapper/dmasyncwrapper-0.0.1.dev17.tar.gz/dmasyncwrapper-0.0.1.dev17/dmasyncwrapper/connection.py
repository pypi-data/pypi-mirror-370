# -*- coding: UTF-8 -*-
import asyncio
import typing

import dmPython

from dmasyncwrapper import consts
from dmasyncwrapper.abstract import AbstractConnection, AbstractPool
from dmasyncwrapper.cursor import Cursor


class Connection(AbstractConnection):

    @classmethod
    def by_pool(
            cls, *, sync_connection: dmPython.Connection, pool: AbstractPool,
    ) -> typing.Self:
        obj = cls(
            host=pool.host, port=pool.port, user=pool.user,
            password=pool.password, auto_commit=pool.auto_commit,
            local_code=pool.local_code)
        obj._sync_connection = sync_connection
        obj._pool = pool
        return obj

    def __init__(
            self, *, host: str, port: int, user: str, password: str,
            auto_commit: bool, local_code: consts.LocalCode,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.auto_commit = auto_commit
        self.local_code = local_code

        self._sync_connection: dmPython.Connection | None = None
        self._pool: AbstractPool | None = None

    async def __aenter__(self) -> typing.Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._pool:
            return await self._pool.release(connection=self)
        else:
            return await self.close()

    async def init(self) -> None:
        if self._sync_connection is not None:
            raise RuntimeError('Connection is already established')
        self._sync_connection = await asyncio.to_thread(
            dmPython.connect,
            host=self.host, port=self.port, user=self.user,
            password=self.password, autoCommit=self.auto_commit)
        if not isinstance(self._sync_connection, dmPython.Connection):
            raise TypeError('Expected dmPython.Connection, got {}'.format(
                type(self._sync_connection)))

    async def close(self):
        return await asyncio.to_thread(self._sync_connection.close)

    async def commit(self):
        return await asyncio.to_thread(self._sync_connection.commit)

    async def rollback(self):
        return await asyncio.to_thread(self._sync_connection.rollback)

    def cursor(self) -> Cursor:
        sync_cursor = self._sync_connection.cursor()
        if not isinstance(sync_cursor, dmPython.Cursor):
            raise TypeError('Expected dmPython.Cursor, got {}'.format(
                type(sync_cursor)))
        return Cursor(sync_cursor=sync_cursor, connection=self)

    async def ping(self, *, reconnect: bool = False) -> None:
        return await asyncio.to_thread(self._sync_connection.ping, reconnect)
