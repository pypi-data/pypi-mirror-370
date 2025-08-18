# -*- coding: UTF-8 -*-
import abc
import typing

from dmasyncwrapper import consts


class AbstractPool(metaclass=abc.ABCMeta):

    def __init__(
            self, *, host: str, port: int, user: str, password: str,
            auto_commit: bool, local_code: consts.LocalCode,
            min_size: int, max_size: int,
    ):
        # Check Parameters
        if min_size <= 0 or max_size <= 0:
            raise ValueError('min_size and max_size must be greater than 0')
        if min_size > max_size:
            raise ValueError('min_size cannot be greater than max_size')

        # Connection Parameters
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.auto_commit = auto_commit
        self.local_code = local_code

        # Pool Parameters
        self.min_size = min_size
        self.max_size = max_size

    @abc.abstractmethod
    def acquire(self) -> 'AbstractConnection':
        ...

    @abc.abstractmethod
    async def release(self, *, connection: 'AbstractConnection'):
        ...


class AbstractConnection(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def __aenter__(self) -> typing.Self:
        ...

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        ...

    @abc.abstractmethod
    async def close(self):
        ...

    @abc.abstractmethod
    async def commit(self):
        ...

    @abc.abstractmethod
    async def rollback(self):
        ...

    @abc.abstractmethod
    def cursor(self) -> 'AbstractCursor':
        ...


class AbstractCursor(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def __aenter__(self) -> typing.Self:
        ...

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        ...

    @abc.abstractmethod
    async def callproc(self, procname: str, *args, **kwargs):
        ...

    @abc.abstractmethod
    async def close(self):
        ...

    @abc.abstractmethod
    async def execute(
            self, operation: str, parameters: typing.Sequence = None,
            *args, **kwargs,
    ):
        ...

    @abc.abstractmethod
    async def executemany(
            self, operation: str,
            seq_of_parameters: typing.Sequence[typing.Sequence] = None,
            *args, **kwargs,
    ):
        ...

    @abc.abstractmethod
    async def fetchone(self) -> tuple | None:
        ...

    @abc.abstractmethod
    async def fetchmany(self, size=None) -> list[tuple]:
        ...

    @abc.abstractmethod
    async def fetchall(self) -> list[tuple]:
        ...

    @abc.abstractmethod
    async def nextset(self):
        ...

    @abc.abstractmethod
    async def setinputsizes(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    async def setoutputsize(self, *args, **kwargs):
        ...
