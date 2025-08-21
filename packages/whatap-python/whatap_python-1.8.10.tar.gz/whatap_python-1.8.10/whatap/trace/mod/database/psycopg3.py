from whatap.trace.mod.application.wsgi import trace_handler
from whatap.trace.mod.database.util import (
    interceptor_db_con, interceptor_db_execute, interceptor_db_close,
    async_interceptor_db_con, async_interceptor_db_execute, async_interceptor_db_close
)

db_info = {}


class BaseCursor:
    def __init__(self, cursor, db_info):
        self._cursor = cursor
        self._db_info = db_info

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            setattr(self._cursor, name, value)

    @property
    def connection(self):
        return self._cursor.connection

    def _execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        def safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return original_execute_method(*args, **kwargs)

        return safe_execute


class SyncCursor(BaseCursor):
    def __enter__(self):
        self._cursor.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._cursor.__exit__(exc_type, exc_val, exc_tb)

    def execute(self, *args, **kwargs):
        real_execute = self._cursor.execute
        safe_fn = self._execute_wrapper(real_execute)

        callback = interceptor_db_execute(safe_fn,self._db_info,self._cursor,*args,**kwargs)

        return callback

    def executemany(self, *args, **kwargs):
        real_executemany = getattr(self._cursor, "executemany", None)

        if real_executemany is None:
            return self._cursor.executemany(*args, **kwargs)

        safe_fn = self._execute_wrapper(real_executemany)

        callback = interceptor_db_execute(safe_fn,self._db_info,self._cursor,*args,**kwargs)

        return callback


class AsyncCursor(BaseCursor):

    async def __aenter__(self):
        await self._cursor.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._cursor.__aexit__(exc_type, exc_val, exc_tb)

    def _async_execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        async def async_safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return await original_execute_method(*args, **kwargs)

        return async_safe_execute

    async def execute(self, *args, **kwargs):
        real_execute = self._cursor.execute
        safe_fn = self._async_execute_wrapper(real_execute)


        callback = await async_interceptor_db_execute(safe_fn,self._db_info,self._cursor,*args,**kwargs)

        return callback

    async def executemany(self, *args, **kwargs):
        real_executemany = getattr(self._cursor, "executemany", None)

        if real_executemany is None:
            return await self._cursor.executemany(*args, **kwargs)

        safe_fn = self._async_execute_wrapper(real_executemany)

        callback = await async_interceptor_db_execute(safe_fn,self._db_info,self._cursor,*args,**kwargs)
        return callback


class BaseConnection:
    def __init__(self, connection, db_info):
        self._connection = connection
        self._db_info = db_info

    def __getattr__(self, name):
        return getattr(self._connection, name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            setattr(self._connection, name, value)

    def _execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        def safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return original_execute_method(*args, **kwargs)

        return safe_execute

    def close(self, *args, **kwargs):
        real_close = self._connection.close

        callback = interceptor_db_close(real_close, *args, **kwargs)
        return callback


class SyncConnection(BaseConnection):

    def __enter__(self):
        self._connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._connection.__exit__(exc_type, exc_val, exc_tb)

    def cursor(self, *args, **kwargs):
        real_cursor = self._connection.cursor(*args, **kwargs)
        return SyncCursor(real_cursor, self._db_info)

    def execute(self, *args, **kwargs):
        real_execute = getattr(self._connection, "execute", None)

        if real_execute is None:
            return self._connection.execute(*args, **kwargs)

        safe_fn = self._execute_wrapper(real_execute)

        callback = interceptor_db_execute(safe_fn,self._db_info,self._cursor,*args,**kwargs)

        return callback


class AsyncConnection(BaseConnection):

    async def __aenter__(self):
        await self._connection.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._connection.__aexit__(exc_type, exc_val, exc_tb)

    def cursor(self, *args, **kwargs):
        real_cursor = self._connection.cursor(*args, **kwargs)
        return AsyncCursor(real_cursor, self._db_info)

    def _async_execute_wrapper(self, original_execute_method):
        owner = getattr(original_execute_method, "__self__", None)

        async def async_safe_execute(*args, **kwargs):
            if args and owner is not None and args[0] is owner:
                args = args[1:]
            return await original_execute_method(*args, **kwargs)

        return async_safe_execute

    async def execute(self, *args, **kwargs):
        real_execute = getattr(self._connection, "execute", None)

        if real_execute is None:
            return await self._connection.execute(*args, **kwargs)

        safe_fn = self._async_execute_wrapper(real_execute)

        callback = await async_interceptor_db_execute(safe_fn,self._db_info,self._connection,*args,**kwargs)

        return callback

    async def close(self, *args, **kwargs):
        real_close = self._connection.close

        callback =  await async_interceptor_db_close(real_close, *args, **kwargs)

        return callback


def _sync_wrapper(fn):

    @trace_handler(fn)
    def wrapper(*args, **kwargs):
        global db_info

        db_info = {"type": "postgresql"}
        db_info.update(kwargs)

        connection = interceptor_db_con(fn, db_info, *args, **kwargs)

        return SyncConnection(connection, dict(db_info))

    return wrapper


def _async_wrapper(fn):

    @trace_handler(fn)
    async def wrapper(*args, **kwargs):
        global db_info

        db_info = {"type": "postgresql"}
        db_info.update(kwargs)

        connection = await async_interceptor_db_con(fn,db_info,*args,**kwargs)

        return AsyncConnection(connection, dict(db_info))

    return wrapper


def instrument_psycopg3(module):
    original_connect = module.connect

    module.connect = _sync_wrapper(original_connect)

    if hasattr(module, 'AsyncConnection'):
        async_conn = module.AsyncConnection

        if hasattr(async_conn, 'connect'):
            original_async_connect = async_conn.connect
            async_conn.connect = _async_wrapper(original_async_connect)

