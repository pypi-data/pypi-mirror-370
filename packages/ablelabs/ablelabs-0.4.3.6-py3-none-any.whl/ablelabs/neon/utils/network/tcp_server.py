from loguru import logger
import asyncio
import time

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.base_tcp import *


class TcpServer(BaseTcp):
    def __init__(
        self,
        name="Server",
        encoding: str = "utf-8",
        log_func: Callable = logger.trace,
    ):
        super().__init__(name=name, encoding=encoding, log_func=log_func)
        self._server: asyncio.Server = None
        self.on_disconnected = None

    async def open(self, ip, port):
        logger.info(f"Waiting for a connection...({ip}:{port})")
        try:
            self._server = await asyncio.start_server(
                self._client_connected_cb, ip, port
            )
        except Exception as e:
            self._is_connected = False

    async def _client_connected_cb(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        self._reader = reader
        self._writer = writer
        client_address = writer.get_extra_info("peername")
        logger.info(f"Connection from {client_address}")
        asyncio.create_task(self.handle_receive())
        self._is_connected = True
        for on_connected in self.on_connected:
            await on_connected()

    async def close(self):
        if not self._server:
            return
        self._server.close()
        await self._server.wait_closed()


async def main():
    # TcpServer.example()

    logger.remove()
    logger.add(sys.stdout, level="TRACE")
    # logger.add(sys.stdout, level="DEBUG")
    logger.add("logs/trace.log", level="TRACE")
    logger.add("logs/debug.log", level="DEBUG")
    logger.add("logs/info.log", level="INFO")

    ip = "localhost"
    port = 1234

    tcp_server = TcpServer(name="tcp_server", log_func=logger.trace)

    async def on_server_received(message: str):
        logger.debug(f"server <- {message}")

    tcp_server.on_received.append(on_server_received)
    await tcp_server.open(ip=ip, port=port)

    from ablelabs.neon.utils.network.tcp_client import TcpClient

    tcp_client = TcpClient(name="tcp_client", log_func=logger.trace)

    async def on_client_received(message: str):
        logger.debug(f"client <- {message}")

    tcp_client.on_received.append(on_client_received)
    await tcp_client.connect(ip=ip, port=port)

    await tcp_server.send("server send to client")
    await tcp_client.send("client send to server")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
