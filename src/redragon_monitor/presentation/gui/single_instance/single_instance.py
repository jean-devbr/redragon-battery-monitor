import os
from typing import Callable

from PySide6.QtNetwork import QLocalServer, QLocalSocket

TIMEOUT_MS = 300
SHOW_MESSAGE = b"show"


class SingleInstance:
    def __init__(self, key: str = f"redragon-battery-monitor-{os.getuid()}"):
        self._key = key
        self._server = QLocalServer()
        self._on_activate: Callable[[], None] = lambda: None

    def notify_running(self) -> bool:
        socket = QLocalSocket()
        socket.connectToServer(self._key)
        if not socket.waitForConnected(TIMEOUT_MS):
            return False
        socket.write(SHOW_MESSAGE)
        socket.waitForBytesWritten(TIMEOUT_MS)
        socket.disconnectFromServer()
        return True

    def listen(self, on_activate: Callable[[], None]) -> None:
        self._on_activate = on_activate
        QLocalServer.removeServer(self._key)
        self._server.listen(self._key)
        self._server.newConnection.connect(self._accept)

    def _accept(self) -> None:
        connection = self._server.nextPendingConnection()
        if connection is None:
            return
        connection.readyRead.connect(lambda: (connection.readAll(), self._on_activate()))
        connection.disconnected.connect(connection.deleteLater)
