import asyncio
from loguru import logger
import pickle
from typing import Callable, Any
import binascii
from functools import update_wrapper
import datetime
import traceback
import cv2
import numpy as np

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.utils.network.tcp_server import TcpServer
from ablelabs.neon.utils.decorators import get_args_dict

IP = "localhost"
PORT = 2345


class Struct:
    def __init__(self, a: int, b: float, c: str) -> None:
        self.a = a
        self.b = b
        self.c = c

    def __str__(self) -> str:
        return f"a={self.a} b={self.b} c={self.c}"


class Messenger:
    ENCODING = "utf-8"

    @staticmethod
    def decode(packet):
        packet_bytes = pickle.dumps(packet)
        packet_hex = binascii.hexlify(packet_bytes)
        return packet_hex.decode(Messenger.ENCODING)
        # return packet_bytes.hex()

    @staticmethod
    def encode(msg: str):
        packet_bytes = binascii.unhexlify(msg)
        return pickle.loads(packet_bytes)

    @staticmethod
    def mat_to_png(image: cv2.Mat):
        retval, buf = cv2.imencode(".png", image)
        return buf

    @staticmethod
    def png_to_mat(buf: np.ndarray[np.uint8]):
        image = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return image

    @staticmethod
    def convert_args_format(args: dict) -> dict:
        """
        cv2.Mat -> PNG
        PNG -> cv2.Mat
        """
        converted_args = {}
        for key, value in args.items():
            if isinstance(value, cv2.Mat):  # cv2.Mat -> PNG
                converted_args[key] = Messenger.mat_to_png(value)
            elif (
                isinstance(value, np.ndarray)
                and value[:8].tobytes() == b"\x89PNG\r\n\x1a\n"  # png_signature
            ):  # PNG -> cv2.Mat
                converted_args[key] = Messenger.png_to_mat(value)
            else:
                converted_args[key] = value
        return converted_args

    @staticmethod
    def to_request_packet(time: datetime.datetime, func: Callable, args: dict):
        args = Messenger.convert_args_format(args)
        packet = (time, func.__name__, args)
        result = Messenger.decode(packet)
        return result

    @staticmethod
    def to_request_tuple(msg: str):
        packet = Messenger.encode(msg)
        (time, func_name, args) = packet
        args = Messenger.convert_args_format(args)
        return (time, func_name, args)

    @staticmethod
    def to_response_packet(time: datetime.datetime, func: Callable, args: dict, rtn):
        args = Messenger.convert_args_format(args)
        packet = (time, func.__name__, args, rtn)
        result = Messenger.decode(packet)
        return result

    @staticmethod
    def to_response_tuple(msg: str):
        packet = Messenger.encode(msg)
        (time, func_name, args, rtn) = packet
        args = Messenger.convert_args_format(args)
        return (time, func_name, args, rtn)


class MessengerServer:
    def __init__(self, tcp_server: TcpServer) -> None:
        self._tcp_server = tcp_server

        async def on_received(msg: str):
            asyncio.create_task(self.execute(msg))

        self._tcp_server.on_received.append(on_received)

    async def execute(self, msg: str):
        (time, func_name, args) = Messenger.to_request_tuple(msg)
        try:
            func = getattr(self, func_name)
        except AttributeError as e:
            send_msg = Messenger.to_response_packet(
                time, func_name, args, NotImplementedError()
            )
        else:
            try:
                rtn = await func(**args)
            except Exception as e:
                e_tb = MessengerServer.extract_traceback(e)
                send_msg = Messenger.to_response_packet(time, func, args, e_tb)
            else:
                send_msg = Messenger.to_response_packet(time, func, args, rtn)
        await self._tcp_server.send(send_msg)

    @staticmethod
    def extract_traceback(e: Exception):
        tb = traceback.extract_tb(e.__traceback__)
        frame = tb[-1]
        filename, lineno, function, text = frame
        filename = str(filename).split("\\")[-1]
        result = type(e)(f"{e}, {filename}, line {lineno}, in {function}, {text}")
        return result


class MessengerClient:
    def __init__(self, tcp_client: TcpClient) -> None:
        self._tcp_client = tcp_client
        self._requests = []

        async def on_received(msg: str):
            if len(self._requests) == 0:
                return
            (time, func_name, args, rtn) = Messenger.to_response_tuple(msg)
            for req in self._requests:
                (req_time, req_func_name, req_args, req_futre) = req
                if (
                    time == req_time
                    and func_name == req_func_name
                    and pickle.dumps(args) == pickle.dumps(req_args)
                ):
                    future: asyncio.Future = req_futre
                    future.set_result(rtn)
                    # try:
                    #     future.set_result(rtn)
                    # except asyncio.exceptions.InvalidStateError as e:
                    #     logger.warning(f"{e} : func={func_name} args={args} rtn={rtn}")
                    self._requests.remove(req)
                # else:
                #     print(f"{time=}")
                #     print(f"{req_time=}")
                #     print(f"{func_name=}")
                #     print(f"{req_func_name=}")
                #     print(f"{args=}")
                #     print(f"{req_args=}")

        self._tcp_client.on_received.append(on_received)

    async def send(self, time: datetime.datetime, func: Callable, args: dict):
        msg = Messenger.to_request_packet(time, func, args)
        await self._tcp_client.send(msg)

    async def request(self, func: Callable, args: dict, wait_return: bool):
        if not self._tcp_client.is_connected():
            raise ConnectionError(f"{MessengerClient.__name__} not connected.")
            # return
        req_time = datetime.datetime.now()
        future = asyncio.Future()
        self._requests.append((req_time, func.__name__, args, future))
        await self.send(time=req_time, func=func, args=args)
        if wait_return:
            await asyncio.gather(future)
            return future.result()
            # try:
            #     await asyncio.gather(future)
            # except InterruptedError as e:
            #     return False
            # # except asyncio.exceptions.InvalidStateError as e:
            # #     logger.error(f"{e}")
            # else:
            #     return future.result()


def run_server_func(
    origin_func: Callable = None,
    wait_return: bool = True,
):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            _func = origin_func if origin_func else func
            if args and isinstance(args[0], MessengerClient):
                self = args[0]
                args = args[1:]
                args_dict = get_args_dict(_func, *args, **kwargs)
                result = await self.request(
                    func=_func,
                    args=args_dict,
                    wait_return=wait_return,
                )
                if isinstance(result, Exception):
                    e_args = {
                        "e": f"{result}",
                        "func": _func.__qualname__,
                        "args": args_dict,
                    }
                    e_args_str = f"{e_args}"
                    # e_args_str = get_dict_str(e_args)
                    e = type(result)(e_args_str)
                    logger.error(e)
                    # raise e from result
                    if isinstance(result, InterruptedError):
                        return e
                    else:
                        raise e from result
                else:
                    return result

        # update_wrapper(wrapper, func)
        return wrapper

    return decorator


class CustomMessengerServer(MessengerServer):
    async def func_a(self, args: Struct):
        import datetime

        logger.info(f"func_a({args}) - 1")
        await asyncio.sleep(1)
        logger.info(f"func_a({args}) - 2")
        return f"args={args} {datetime.datetime.now()}"

    async def func_a2(self, args: Struct):
        import datetime

        logger.info(f"func_b({args}) - 1")
        await asyncio.sleep(1)
        logger.info(f"func_b({args}) - 2")
        return f"args={args} {datetime.datetime.now()}"

    async def func_exception(self):
        a = 0 / 0


class CustomMessengerClient(MessengerClient):
    @run_server_func()
    async def func_a(self, args: Struct):
        pass

    @run_server_func(CustomMessengerServer.func_a2)
    async def func_b(self, args: Struct):
        pass

    @run_server_func(CustomMessengerServer.func_exception)
    async def func_exception(self):
        pass


async def main():
    logger.remove()
    # logger.add(sys.stdout, level="TRACE")
    logger.add(sys.stdout, level="DEBUG", backtrace=False)
    # logger.add(sys.stdout, level="INFO")
    logger.add("logs/trace.log", level="TRACE")
    logger.add("logs/debug.log", level="DEBUG")
    logger.add("logs/info.log", level="INFO")

    tcp_server = TcpServer()
    tcp_client = TcpClient()
    await tcp_server.open(ip=IP, port=PORT)
    await tcp_client.connect(ip=IP, port=PORT)
    server = CustomMessengerServer(tcp_server)
    client = CustomMessengerClient(tcp_client)
    # logger.info(await client.func_a(args=Struct(a=1, b=2.345, c="c")))
    # logger.info(await client.func_a(args=Struct(a=2, b=2.345, c="cc")))
    # logger.info(await client.func_a(args=Struct(a=3, b=2.345, c="ccc")))
    # logger.info(await client.func_a(args=Struct(a=4, b=2.345, c="cccc")))
    # logger.info(await client.func_b(args=Struct(a=1, b=2.345, c="c")))
    # logger.info(await client.func_b(args=Struct(a=2, b=2.345, c="cc")))
    # logger.info(await client.func_b(args=Struct(a=3, b=2.345, c="ccc")))
    # logger.info(await client.func_b(args=Struct(a=4, b=2.345, c="cccc")))

    # logger.info("start")
    # task = asyncio.create_task(client.func_a(args=Struct(a=9, b=9.9, c="9")))
    # task2 = asyncio.create_task(client.func_a(args=Struct(a=9, b=9.9, c="9")))
    # results = await asyncio.gather(task, task2)
    # logger.info(f"end : {results}")

    tasks = [
        asyncio.create_task(async_func)
        for async_func in [
            client.func_a(args=Struct(a=9, b=9.9, c="9")),
            client.func_b(args=Struct(a=99, b=99.9, c="99")),
            client.func_exception(),
        ]
    ]
    while not all([task.done() for task in tasks]):
        print("waiting...")
        await asyncio.sleep(0.1)
    results = [task.result() for task in tasks]
    logger.info(f"end : {results}")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    # loop.set_debug(True)
    loop.create_task(main())
    loop.run_forever()
