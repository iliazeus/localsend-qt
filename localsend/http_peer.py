from dataclasses import asdict
import json
import sys
from typing import cast

from PySide6.QtCore import QObject, Signal

from PySide6.QtNetwork import (
    QHostAddress,
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkReply,
    QSslConfiguration,
    QSslSocket,
    QTcpServer,
)

from PySide6.QtHttpServer import (
    QHttpServer,
    QHttpServerRequest,
)

from .dto import AnnouncementDto
from .peer_info import PeerInfo
from .remote_peer_info import RemotePeerInfo


class _HttpClient(QObject):
    _manager: QNetworkAccessManager

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._manager = QNetworkAccessManager(self)

    def _makeRequest(self) -> QNetworkRequest:
        req = QNetworkRequest()

        req.setHeader(req.KnownHeaders.UserAgentHeader, "localsend-qt/0.1.0")
        req.setHeader(req.KnownHeaders.ContentTypeHeader, "application/json")

        ssl_config = QSslConfiguration()
        ssl_config.setPeerVerifyMode(QSslSocket.PeerVerifyMode.QueryPeer)
        req.setSslConfiguration(ssl_config)

        return req

    def register(self, remotePeerInfo: RemotePeerInfo, localPeerInfo: PeerInfo):
        url = remotePeerInfo.url
        url.setPath("/api/localsend/v2/register")

        req = self._makeRequest()
        req.setUrl(url)

        payload = localPeerInfo.makeAnnouncement()
        payload = json.dumps(asdict(payload)).encode()

        reply = self._manager.post(req, payload)
        reply.finished.connect(self._onReplyFinished)

    def _onReplyFinished(self):
        STATUS_CODE = QNetworkRequest.Attribute.HttpStatusCodeAttribute
        REASON_PHRASE = QNetworkRequest.Attribute.HttpReasonPhraseAttribute

        reply = cast(QNetworkReply, self.sender())
        reply.deleteLater()

        if reply.error() != reply.NetworkError.NoError:
            url = reply.url().toString()
            err = reply.errorString()
            print(f"{url} {err}", file=sys.stderr)
            return

        status_code: int = reply.attribute(STATUS_CODE)
        if status_code >= 300:
            url = reply.url().toString()
            reason_phrase: str = reply.attribute(REASON_PHRASE)
            print(f"{url} {status_code} {reason_phrase}", file=sys.stderr)
            return


class HttpPeer(QObject):
    PORT = 53317

    _instance: HttpPeer | None = None

    _tcpServer: QTcpServer
    _httpServer: QHttpServer

    _client: _HttpClient

    remotePeerRegistered = Signal(RemotePeerInfo)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        assert HttpPeer._instance is None
        HttpPeer.instance = self

        self._tcpServer = QTcpServer(self)
        assert self._tcpServer.listen(QHostAddress.SpecialAddress.Any, self.PORT)

        self._httpServer = QHttpServer(self)
        self._httpServer.route("/api/localsend/v2/register", self._handleRegister)
        assert self._httpServer.bind(self._tcpServer)

        self._client = _HttpClient(self)

    @staticmethod  # W/A; TODO: better solution?
    def _handleRegister(req: QHttpServerRequest):
        payload = json.loads(req.body().toStdString())
        payload = AnnouncementDto(**payload)

        print(f"received register request from {payload.alias}", file=sys.stderr)

        remote_peer_info = RemotePeerInfo(
            address=req.remoteAddress(),
            info=PeerInfo.fromAnnouncement(payload),
        )

        HttpPeer.instance.remotePeerRegistered.emit(remote_peer_info)

        return '{ "ok": true }'

    def register(self, remotePeerInfo: RemotePeerInfo, localPeerInfo: PeerInfo):
        self._client.register(remotePeerInfo, localPeerInfo)
