import functools
import inspect
from types import AsyncGeneratorType

from fishhook import hook


def is_generator(gen):
    return inspect.isgenerator(gen)

def is_coroutine(coro):
    return inspect.iscoroutine(coro)

class YieldStop:
    pass


@hook(AsyncGeneratorType)
def __iter__(self):
    exhausted = False
    async def advance_async_iterator():
        try:
            out = await anext(self)
        except StopAsyncIteration:
            nonlocal exhausted
            exhausted = True
            out = YieldStop
        return out
    while not exhausted:
        yield advance_async_iterator()


def prime_generator(gen):
    try:
        out = next(gen)
    except StopIteration as ex:
        out = ex.value
    return out


def exhaust_by_identity(gen):
    out = prime_generator(gen)
    while True:
        try:
            out = exhaust_by_identity(out) if is_generator(out) else out
            out = gen.send(out)
        except StopIteration as ex:
            out = ex.value or out
            break
        except Exception as ex:
            out = gen.throw(ex)
    return out


def yield_to_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        return exhaust_by_identity(gen)
    return wrapper


async def exhaust_by_await(gen):
    out = prime_generator(gen)
    while True:
        try:
            out = await exhaust_by_await(out) if is_generator(out) else out
            out = await out if is_coroutine(out) else out
            out = gen.send(out)
        except StopIteration as ex:
            out = ex.value or out
            break
        except Exception as ex:
            out = gen.throw(ex)
    return out


def yield_to_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        gen = await func(*args, **kwargs)
        return await exhaust_by_await(gen)
    return wrapper
