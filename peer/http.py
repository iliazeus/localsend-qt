from dataclasses import asdict
import json
import sys

from PySide6.QtCore import QByteArray, QObject, Signal, Slot
from PySide6.QtHttpServer import QHttpServer, QHttpServerRequest
from PySide6.QtNetwork import (
    QHostAddress,
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkReply,
    QSslConfiguration,
    QSslSocket,
    QTcpServer,
)


from peer.common import *


class HttpPeer(QObject):
    instance: HttpPeer = None  # type: ignore

    REGISTER_ENDPOINT = "/api/localsend/v2/register"

    _tcp_server: QTcpServer
    _http_server: QHttpServer

    _na_manager: QNetworkAccessManager

    remote_peer_registered = Signal(object)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        assert HttpPeer.instance is None
        HttpPeer.instance = self

        self._tcp_server = QTcpServer(self)
        assert self._tcp_server.listen(QHostAddress.SpecialAddress.Any, PORT)

        self._http_server = QHttpServer(self)
        assert self._http_server.route(
            self.REGISTER_ENDPOINT,
            self._handle_register,
        )
        assert self._http_server.bind(self._tcp_server)

        self._na_manager = QNetworkAccessManager(self)

    @staticmethod
    def _handle_register(req: QHttpServerRequest) -> str:
        peer = RemotePeer(
            req.remoteAddress().toString(),
            PeerInfo(**json.loads(req.body().toStdString())),
        )
        HttpPeer.instance.remote_peer_registered.emit(peer)
        return '{ "ok": true }'

    def get_url(self, remote_peer: RemotePeer) -> str:
        scheme = remote_peer.info.protocol
        host = remote_peer.address
        if ":" in host:
            host = "[" + host + "]"
        port = remote_peer.info.port
        path = self.REGISTER_ENDPOINT
        return f"{scheme}://{host}:{port}{path}"

    def register(self, remote_peer: RemotePeer, local_info: PeerInfo):
        req = QNetworkRequest()
        req.setUrl(self.get_url(remote_peer))
        req.setHeader(req.KnownHeaders.ContentTypeHeader, "application/json")

        body = QByteArray.fromStdString(json.dumps(asdict(local_info)))

        ssl_config = QSslConfiguration()
        ssl_config.setPeerVerifyMode(QSslSocket.PeerVerifyMode.QueryPeer)
        req.setSslConfiguration(ssl_config)

        reply = self._na_manager.post(req, body)
        reply.finished.connect(self._on_register_response)

    @Slot()
    def _on_register_response(self):
        reply: QNetworkReply = self.sender()  # type: ignore
        if reply.error() != QNetworkReply.NetworkError.NoError:
            print(reply.url().toString() + ": " + reply.errorString(), file=sys.stderr)
        reply.deleteLater()
