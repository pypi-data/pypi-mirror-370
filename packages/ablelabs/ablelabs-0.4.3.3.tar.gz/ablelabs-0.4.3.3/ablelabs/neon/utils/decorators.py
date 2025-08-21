from dataclasses import dataclass
import time
from typing import Callable
import asyncio
import inspect
from functools import update_wrapper
import numpy as np


def log_elapsed_time(log_func: Callable):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            log_func(f"{func.__name__} : {elapsed_time*1e3:.1f} ms")
            return result

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


def log_elapsed_time_async(log_func: Callable):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            log_func(f"{func.__name__} : {elapsed_time*1e3:.1f} ms")
            return result

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


@log_elapsed_time(print)
def test_check_time(n):
    for _ in range(n):
        time.sleep(0.01)


@log_elapsed_time_async(print)
async def test_check_time_async(n):
    for _ in range(n):
        await asyncio.sleep(0.01)


def get_args_dict(func: Callable, *args, **kwargs):
    sig = inspect.signature(func)
    try:  # sypark 여기 try문을 다른 걸로 대체할 수 없을까?
        bound = sig.bind(*args, **kwargs)
    except:
        bound = sig.bind(None, *args, **kwargs)
    # if "self" in sig.parameters:
    #     bound = sig.bind(None, *args, **kwargs)
    # else:
    #     bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    result = dict(bound.arguments)
    if "self" in result and result["self"] is None:
        del result["self"]
    return result


def str_value(value, max_len: int = None, level: int = 0, max_level: int = 0):
    """
    객체를 문자열로 변환하며, 너무 긴 경우 줄임표로 요약하는 함수.

    Args:
    - value: 변환할 값 (list, dict, tuple, 기본 타입 등)
    - max_len: 출력할 최대 길이
    - level: 현재 중첩 수준 (기본값: 0)
    - max_level: 문자열을 줄이기 시작할 중첩 수준 (기본값: 1)

    Returns:
    - str: 요약된 문자열 표현
    """

    # 중첩 수준에 따른 문자열 요약 처리
    if isinstance(value, list):
        # 리스트일 경우
        value_str = (
            "["
            + ", ".join(str_value(v, max_len, level + 1, max_level) for v in value)
            + "]"
        )
    elif isinstance(value, dict):
        # 딕셔너리일 경우
        value_str = (
            "{"
            + ", ".join(
                f"{str_value(k, max_len, level + 1, max_level)}: {str_value(v, max_len, level + 1, max_level)}"
                for k, v in value.items()
            )
            + "}"
        )
    elif isinstance(value, tuple):
        # 튜플일 경우
        value_str = (
            "("
            + ", ".join(str_value(v, max_len, level + 1, max_level) for v in value)
            + ")"
        )
    elif inspect.iscoroutine(value):
        # Coroutine 객체의 경우
        value_str = value.__qualname__
    elif isinstance(value, asyncio.Task):
        # 비동기 Task 객체의 경우
        value_str = value.get_coro().__qualname__
    elif isinstance(value, np.ndarray):
        height, width = value.shape[:2]
        channels = value.shape[2] if len(value.shape) == 3 else 1
        data_type = value.dtype
        value_str = f"{height}x{width}({channels}ch,{data_type})"
    else:
        # 기본 타입일 경우
        value_str = str(value)

    # 줄바꿈 문자를 제거하고 공백으로 대체
    value_str = value_str.replace("\r", "").replace("\n", "")

    # 중첩 수준에 따라 문자열을 자르고, 요약된 길이를 출력
    if max_len and len(value_str) > max_len and level >= max_level:
        value_str = value_str[:max_len] + " ..."
        if isinstance(value, list):
            value_str += f" (len: {len(value)})"
        elif isinstance(value, dict):
            value_str += f" (len: {len(value)})"
        elif isinstance(value, tuple):
            value_str += f" (len: {len(value)})"

    return value_str


def get_dict_str(value: dict):
    args_strs = []
    for key, value in value.items():
        args_strs.append(f"{key}={str_value(value)}")
    result = f"{' '.join(args_strs)}"
    return result


def get_func_args_str(func: Callable, args_dict: dict, max_len: int = None):
    # args_strs = [f"{k}={v}" for k, v in args_dict.items() if k != "self"]
    args_strs = []
    for key, value in args_dict.items():
        if key == "self":
            continue
        args_strs.append(f"{key}={str_value(value, max_len=max_len)}")
    result = f"{func.__name__}({' '.join(args_strs)})"
    return result


def log_func_args(
    log_before_func: Callable = None,
    log_after_func: Callable = None,
    max_len: int = None,
):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            args_dict = get_args_dict(func, *args, **kwargs)
            func_args_strs = get_func_args_str(func, args_dict, max_len)
            if log_before_func:
                log_before_func(f"{func_args_strs}")
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                if log_before_func:
                    log_before_func(f"{func_args_strs} : {e}")
                elif log_after_func:
                    log_after_func(f"{func_args_strs} : {e}")
                raise e
            if log_after_func:
                log_after_func(f"{func_args_strs} -> {str_value(result, max_len=50)}")
            return result

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


def log_func_args_async(
    log_before_func: Callable = None,
    log_after_func: Callable = None,
    max_len: int = None,
):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            args_dict = get_args_dict(func, *args, **kwargs)
            func_args_strs = get_func_args_str(func, args_dict, max_len)
            if log_before_func:
                log_before_func(f"{func_args_strs}")
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                if log_before_func:
                    log_before_func(f"{func_args_strs} : {e}")
                elif log_after_func:
                    log_after_func(f"{func_args_strs} : {e}")
                raise e
            if log_after_func:
                log_after_func(f"{func_args_strs} -> {str_value(result, max_len=50)}")
            return result

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


# @log_elapsed_time_async(print)
@log_func_args_async(log_before_func=print, log_after_func=print)
async def test_log_func_args_async(a: int, b: float, c: str):
    await asyncio.sleep(0.01)


def skip_func_async(skip_func: Callable[[], bool], return_value=None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if skip_func():
                return return_value
            return await func(*args, **kwargs)

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


@skip_func_async(skip_func=lambda: True, return_value="return_sample")
async def test_skip_func_async_do_skip():
    print(f"{test_skip_func_async_do_skip.__name__}")


@skip_func_async(skip_func=lambda: False, return_value="return_sample")
async def test_skip_func_async_donot_skip():
    print(f"{test_skip_func_async_donot_skip.__name__}")


@log_func_args(log_before_func=print, log_after_func=print)
def test_long_args(v):
    pass


async def main():
    # test_check_time(1)
    # test_check_time(2)
    # test_check_time(3)

    # await test_check_time_async(1)
    # await test_check_time_async(2)
    # await test_check_time_async(3)

    # await test_log_func_args_async(a=1, b=2.3, c="abc")
    # await test_log_func_args_async(a=0, b=0, c="")
    # await test_log_func_args_async(1, 2.3, "abc")

    # print(await test_skip_func_async_do_skip())
    # print(await test_skip_func_async_donot_skip())

    # num_contours = 5
    # max_points = 100
    # img_size = (500, 500)
    # contours = []
    # for _ in range(num_contours):
    #     # 윤곽선을 구성할 점의 수를 임의로 결정 (최소 4개 이상의 점을 가진 다각형 생성)
    #     num_points = np.random.randint(4, max_points)
    #     # 윤곽선을 구성할 (x, y) 좌표를 임의로 생성
    #     points = np.random.randint(0, min(img_size), size=(num_points, 1, 2))
    #     # 생성된 좌표를 numpy 배열로 변환하여 contours에 추가
    #     contours.append(points.astype(np.int32))
    # test_long_args(contours)

    @dataclass
    class Info:
        a: int
        b: tuple[float, float]
        c: list[str]

    info = Info(a=1, b=(2.3, 3.4), c=[f"{v}" for v in range(1000)])
    infos = [info for _ in range(10)]
    test_long_args(info)
    test_long_args(infos)


if __name__ == "__main__":
    asyncio.run(main())
