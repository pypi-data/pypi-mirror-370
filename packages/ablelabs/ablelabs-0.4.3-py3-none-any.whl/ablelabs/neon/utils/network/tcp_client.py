import datetime
import socket
import threading
import json
from loguru import logger
import asyncio

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.base_tcp import *


class TcpClient(BaseTcp):
    def __init__(
        self,
        name="Client",
        encoding: str = "utf-8",
        log_func: Callable = logger.trace,
    ):
        super().__init__(name=name, encoding=encoding, log_func=log_func)

    async def connect(self, ip, port):
        self._reader, self._writer = await asyncio.open_connection(ip, port)
        self._is_connected = True
        try:
            asyncio.create_task(
                self.handle_receive(), name=self.handle_receive.__name__
            )
        except Exception as e:
            logger.exception(f"{e}")
        for on_connected in self.on_connected:
            await on_connected()


# if __name__ == "__main__":
#     TcpClient.example()
