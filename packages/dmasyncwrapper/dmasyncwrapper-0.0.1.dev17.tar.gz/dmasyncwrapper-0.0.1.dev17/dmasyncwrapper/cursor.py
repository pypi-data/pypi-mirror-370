# -*- coding: UTF-8 -*-
import asyncio
import typing

import dmPython

from dmasyncwrapper.abstract import AbstractConnection, AbstractCursor


class Cursor(AbstractCursor):

    def __init__(
            self, *, sync_cursor: dmPython.Cursor,
            connection: AbstractConnection,
    ):
        self._sync_cursor: dmPython.Cursor = sync_cursor
        self._connection: AbstractConnection = connection

    @property
    def description(self):
        return self._sync_cursor.description

    @property
    def rowcount(self):
        return self._sync_cursor.rowcount

    async def callproc(self, procname, *args, **kwargs):
        return await asyncio.to_thread(
            self._sync_cursor.callproc, procname, *args, **kwargs)

    async def close(self):
        return await asyncio.to_thread(self._sync_cursor.close)

    async def execute(
            self, operation: str, parameters: typing.Sequence = None ,
            *args, **kwargs,
    ):
        return await asyncio.to_thread(
            self._sync_cursor.execute, operation, parameters,
            *args, **kwargs)

    async def executemany(
            self, operation: str,
            seq_of_parameters: typing.Sequence[typing.Sequence] = None,
            *args, **kwargs,
    ):
        return await asyncio.to_thread(
            self._sync_cursor.executemany, operation, seq_of_parameters,
            *args, **kwargs)

    async def fetchone(self) -> tuple | None:
        return await asyncio.to_thread(self._sync_cursor.fetchone)

    async def fetchmany(self, size=None):
        if size is None:
            size = self._sync_cursor.arraysize
        return await asyncio.to_thread(self._sync_cursor.fetchmany, size)

    async def fetchall(self) -> list[tuple]:
        return await asyncio.to_thread(self._sync_cursor.fetchall)

    async def nextset(self):
        return await asyncio.to_thread(self._sync_cursor.nextset)

    @property
    def arraysize(self):
        return self._sync_cursor.arraysize

    async def setinputsizes(self, *args, **kwargs):
        return await asyncio.to_thread(
            self._sync_cursor.setinputsizes, *args, **kwargs)

    async def setoutputsize(self, *args, **kwargs):
        return await asyncio.to_thread(
            self._sync_cursor.setoutputsize, *args, **kwargs)

    async def __aenter__(self) -> typing.Self:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.close()
