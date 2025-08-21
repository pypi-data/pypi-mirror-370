from typing import Any, Callable
import asyncio
from functools import update_wrapper

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.decorators import (
    log_func_args_async,
    get_args_dict,
    get_func_args_str,
)


class Work:
    def __init__(self, func: Callable, args: dict) -> None:
        self.func = func
        self.args = args

    def __str__(self) -> str:
        return get_func_args_str(self.func, self.args)

    async def execute(self):
        func: Callable = self.func
        args = self.args
        try:
            if isinstance(args, dict):
                return await func(**args)
            elif isinstance(args, tuple):
                return await func(*args)
            else:
                return await func(args)
        # to_ 함수인 경우, 리턴이 list라서 await가 안 걸려서 TypeError 발생.
        except TypeError as e:
            pass


class WorkNode:
    def __init__(
        self,
        work: Work,
        children: list = None,
        log_before_func: Callable = None,
        log_after_func: Callable = None,
    ) -> None:
        self.work = work
        self.children: list[WorkNode] = children or []
        self.log_before_func = log_before_func
        self.log_after_func = log_after_func

    def __str__(self) -> str:
        return f"{self.work}"

    def get_all_work_node_str(self):
        str_list = self._get_all_work_node_strs()
        return "\n".join(str_list)

    def _get_all_work_node_strs(self, depth=0):
        result = ["\t" * depth + f"{self.work}"]
        for child in self.children:
            result.extend(child._get_all_work_node_strs(depth + 1))
        return result


def to_work_node(
    origin_func: Callable = None,
    log_before_func: Callable = None,
    log_after_func: Callable = None,
):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            _func = origin_func if origin_func else func
            args_dict = get_args_dict(_func, *args, **kwargs)
            children = func(**args_dict)
            result = WorkNode(
                work=Work(_func, args_dict),
                children=children,
                log_before_func=log_before_func,
                log_after_func=log_after_func,
            )
            return result

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


def serialize(work_node: WorkNode):
    work_nodes: list[WorkNode] = (
        work_node if isinstance(work_node, list) else [work_node]
    )
    result: list[Work] = []
    for _work_node in work_nodes:
        result.append(_work_node.work)
        if childs := serialize(_work_node.children):
            if log_func := _work_node.log_before_func:
                result.append(Work(func=log_func, args=f"{_work_node.work}"))
            result.extend(childs)
            if log_func := _work_node.log_after_func:
                result.append(Work(func=log_func, args=f"{_work_node.work} -> done"))
    return result


async def execute_work_node(work_node: WorkNode | list[WorkNode]):
    works = serialize(work_node)
    for work in works:
        await work.execute()


def async_work_node_executor(work_node_method: Callable[[Any], list[WorkNode]]):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            work_node = work_node_method(*args, **kwargs)
            return await execute_work_node(work_node)

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


@log_func_args_async(log_before_func=print, log_after_func=print)
async def test_simple_func(delay: float):
    await asyncio.sleep(delay)


@to_work_node(test_simple_func)
def test_to_simple_func(delay: float) -> Work:
    pass


@to_work_node(log_before_func=print, log_after_func=print)
def test_to_complex_func(a: float, b: float, c: float):
    res: list[WorkNode] = []
    res.append(test_to_simple_func(delay=a))
    res.append(test_to_simple_func(b))
    res.append(test_to_simple_func(delay=c))
    return res


@async_work_node_executor(test_to_complex_func)
def test_complex_func(a: float, b: float, c: float):
    pass


@to_work_node(log_before_func=print, log_after_func=print)
def test_to_more_complex_func(a: float, b: float, c: float, d: float, e: float):
    res: list[WorkNode] = []
    res.append(test_to_simple_func(delay=a))
    res.append(test_to_complex_func(b, b=c, c=d))
    res.append(test_to_simple_func(e))
    return res


@async_work_node_executor(test_to_more_complex_func)
def test_more_complex_func(a: float, b: float, c: float, d: float, e: float):
    pass


async def main():
    # await test_simple_func(delay=1)
    # print(simple_work_node := test_to_simple_func(delay=1))
    # await execute_work_node(simple_work_node)

    # print(complex_work_node := test_to_complex_func(1, b=2, c=3))
    # print(await execute_work_node(complex_work_node))
    # print(
    #     more_complex_work_node := test_to_more_complex_func(
    #         a=0.1, b=0.2, c=0.3, d=0.4, e=0.5
    #     )
    # )
    # print(await execute_work_node(more_complex_work_node))

    # await test_complex_func(1, b=2, c=3)
    # await test_more_complex_func(0.1, b=0.2, c=0.3, d=0.4, e=0.5)

    # complex_work_node = test_to_complex_func(a=1, b=2, c=3)
    # print(complex_work_node)
    # await execute_work_node(complex_work_node)
    more_complex_work_node: WorkNode = test_to_more_complex_func(
        0.1, b=0.2, c=0.3, d=0.4, e=0.5
    )
    print(more_complex_work_node.get_all_work_node_str())
    await execute_work_node(more_complex_work_node)


if __name__ == "__main__":
    asyncio.run(main())
