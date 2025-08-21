import asyncio
from typing import Callable
from loguru import logger
import json


ACK = "[ACK]"
ETX = "\x03"


class BaseTcp:
    def __init__(
        self,
        name: str,
        encoding: str = "utf-8",
        log_func: Callable = logger.trace,
    ) -> None:
        self._name = name
        self._encoding = encoding
        self._log_func = log_func
        self._is_connected = False
        self._reader: asyncio.StreamReader = None
        self._writer: asyncio.StreamWriter = None
        self.on_connected: list[Callable[[],]] = []
        self.on_received: list[Callable[[str],]] = []

    async def disconnect(self):
        if not self.is_connected():
            return
        self._is_connected = False
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as e:
                logger.exception(f"{e}")
                pass

    def is_connected(self):
        # return self._sock is not None and self._is_connected
        return self._is_connected

    async def send(self, message, do_log: bool = True):
        if not self.is_connected():
            return
        if do_log and self._log_func:
            self._log_func(f"[{self._name}] -> {message}")
        message = self._check_json_format(message)
        byte_message = bytearray(f"{message}{ETX}", self._encoding)
        try:
            self._writer.write(byte_message)
            await self._writer.drain()
        except asyncio.CancelledError as e:
            logger.warning(f"Exception: {e}")
            await self.disconnect()

    @staticmethod
    def _check_json_format(value: str | dict):
        if type(value) == str:
            try:
                value_json = json.loads(value)
                result = json.dumps(value_json)
            except:
                result = value
        elif type(value) == dict:
            result = json.dumps(value)
        else:
            result = value
        return result

    # def request(self, message):
    #     self.

    async def handle_receive(self):
        input_buffer = ""
        while self.is_connected():
            try:
                input = await self._reader.read(1024)
                if not input:
                    await self.disconnect()
                input_buffer += input.decode(self._encoding)
                while ETX in input_buffer:
                    idx = input_buffer.find(ETX)
                    temp = input_buffer[:idx]
                    input_buffer = input_buffer[idx + 1 :]

                    message = temp.split(ETX)
                    for m in message:
                        if m.find(ACK) == 0:
                            continue
                        if self._log_func:
                            self._log_func(f"[{self._name}] <- {m}")
                        await self.send(f"{ACK}{m}", do_log=False)
                        for on_received in self.on_received:
                            await on_received(m)
            except (
                ConnectionResetError,
                ConnectionAbortedError,
                asyncio.IncompleteReadError,
            ) as e:
                logger.warning(f"Exception: {e}")
                await self.disconnect()
                return
            except Exception as e:
                logger.exception(f"Exception: {e}", e)
