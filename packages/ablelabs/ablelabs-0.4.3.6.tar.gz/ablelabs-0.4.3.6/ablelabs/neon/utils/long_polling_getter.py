import asyncio
from typing import Optional, TypeVar, Generic

T = TypeVar("T")


class LongPollingGetter(Generic[T]):
    def __init__(self, initial_value: Optional[T] = None):
        self._value: Optional[T] = initial_value
        self._event = asyncio.Event()
        if initial_value is not None:
            self._event.set()

    async def get(self) -> T:
        await self._event.wait()
        self._event.clear()
        return self._value
        # try:
        #     await self._event.wait()
        # # except asyncio.CancelledError as e:
        # #     pass
        # finally:
        #     self._event.clear()
        #     return self._value

    def set(self, value: T) -> None:
        self._value = value
        self._event.set()

    def __add__(self, other: T):
        if self._value is None:
            raise ValueError("Value is not set yet")
        if not isinstance(other, type(self._value)):
            raise TypeError(f"Cannot add {type(other)} to {type(self._value)}")
        new_value = self._value + other
        self.set(new_value)
        return self


async def main():
    a: LongPollingGetter[int] = LongPollingGetter()
    b: LongPollingGetter[float] = LongPollingGetter()
    c: LongPollingGetter[str] = LongPollingGetter()

    async def get_a():
        while True:
            print(f"a = {await a.get()}")

    async def get_b():
        while True:
            print(f"b = {await b.get()}")

    async def get_c():
        while True:
            print(f"c = {await c.get()}")

    tasks = [
        asyncio.create_task(task)
        for task in [
            get_a(),
            get_b(),
            get_c(),
        ]
    ]

    a.set(1)
    await asyncio.sleep(1)
    b.set(2.3)
    await asyncio.sleep(1)
    c.set("c")
    await asyncio.sleep(1)
    a += 1
    b.set(2.33)
    c.set("cc")
    await asyncio.sleep(1)
    a.set(1)
    b.set(2.333)
    c.set("ccc")


if __name__ == "__main__":
    asyncio.run(main())
