# -*- coding: UTF-8 -*-
import asyncio
import collections
import contextlib
import typing

import dmPython

from dmasyncwrapper import consts
from dmasyncwrapper.abstract import AbstractPool
from dmasyncwrapper.connection import Connection

type _AvailConnsT = collections.deque[Connection]


class Pool(AbstractPool):

    def __init__(
            self, *, host: str, port: int, user: str, password: str,
            auto_commit: bool, local_code: consts.LocalCode,
            min_size: int, max_size: int,
    ):
        super().__init__(
            host=host, port=port, user=user, password=password,
            auto_commit=auto_commit, local_code=local_code,
            min_size=min_size, max_size=max_size)

        # Pool State
        self._closed = False
        self._available_connections: _AvailConnsT = collections.deque(
            maxlen=self.max_size)
        self._in_use_connections: set[Connection] = set()
        self._condition = asyncio.Condition()

    async def _make_connection(self) -> Connection:
        sync_connection = await asyncio.to_thread(
            dmPython.connect,
            host=self.host, port=self.port, user=self.user,
            password=self.password, autoCommit=self.auto_commit,
            local_code=self.local_code)
        if not isinstance(sync_connection, dmPython.Connection):
            raise TypeError('Expected dmPython.Connection, got {}'.format(
                type(sync_connection)))
        return Connection.by_pool(sync_connection=sync_connection, pool=self)

    async def init(self) -> None:
        if self._closed:
            raise RuntimeError('Pool is closed')
        if self._available_connections or self._in_use_connections:
            raise RuntimeError('Pool is already initialized')
        coroutines = [self._make_connection() for _ in range(self.min_size)]
        connections = await asyncio.gather(*coroutines)
        self._available_connections.extend(connections)

    async def close(self) -> None:
        self._closed = True
        async with self._condition:
            while self._available_connections:
                connection = self._available_connections.popleft()
                await connection.close()
            await self._condition.wait_for(
                lambda: not self._in_use_connections)
            while self._available_connections:
                connection = self._available_connections.popleft()
                await connection.close()
            self._condition.notify()

    def _check_acquirable(self) -> bool:
        if self._available_connections:
            return True
        if len(self._in_use_connections) < self.max_size:
            return True
        return False

    @contextlib.asynccontextmanager
    async def acquire(self) -> typing.AsyncGenerator[Connection]:
        if self._closed:
            raise RuntimeError('Pool is closed')
        async with self._condition:
            await self._condition.wait_for(self._check_acquirable)
            if self._available_connections:
                connection = self._available_connections.popleft()
            else:
                connection = await self._make_connection()
            self._in_use_connections.add(connection)
        async with connection:
            yield connection

    async def release(self, *, connection: Connection) -> None:
        async with self._condition:
            if connection not in self._in_use_connections:
                raise ValueError('Connection not belong to this pool')
            if connection in self._available_connections:
                raise ValueError('Connection is already available in the pool')
            self._in_use_connections.remove(connection)
            self._available_connections.append(connection)
            self._condition.notify()
