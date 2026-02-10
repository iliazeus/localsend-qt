import secrets

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtQml import ListProperty
from PySide6.QtNetwork import QHostAddress

from names_generator import generate_name

from .http_peer import HttpPeer
from .peer_info import PeerInfo
from .remote_peer_info import RemotePeerInfo
from .udp_peer import UdpPeer
from .util import Property, QmlElement


QML_IMPORT_NAME = "lol.iliazeus.localsend"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Peer(QObject):
    _info: PeerInfo

    _httpPeer: HttpPeer
    _udpPeer: UdpPeer

    _remotePeers: list[RemotePeerInfo]

    @Property(PeerInfo, constant=True)
    def info(self) -> PeerInfo:
        return self._info

    remotePeersChanged = Signal()

    @Property(list, notify=remotePeersChanged)
    def remotePeers(self) -> list[RemotePeerInfo]:
        return self._remotePeers

    # def remotePeer(self, i: int) -> RemotePeerInfo:
    #     return self._remotePeers[i]

    # def remotePeerCount(self) -> int:
    #     return len(self._remotePeers)

    # remotePeers = ListProperty(
    #     RemotePeerInfo,
    #     at=remotePeer,
    #     count=remotePeerCount,
    #     notify=remotePeersChanged,  # type: ignore
    # )

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self._info = PeerInfo(
            parent=self,
            alias=generate_name("capital"),
            version="2.0",
            fingerprint=secrets.token_urlsafe(),
            port=HttpPeer.PORT,
            protocol="http",
            deviceModel=None,
            deviceType="desktop",
            download=False,
        )

        self._remotePeers = []

        self._httpPeer = HttpPeer(self)
        self._httpPeer.remotePeerRegistered.connect(self._onRemotePeerRegistered)

        self._udpPeer = UdpPeer(self, info=self._info)
        self._udpPeer.remotePeerAnnounced.connect(self._onRemotePeerAnnounced)

    @Slot(RemotePeerInfo)
    def _onRemotePeerRegistered(self, remotePeerInfo: RemotePeerInfo):
        for peer in self._remotePeers:
            if peer.info.fingerprint == remotePeerInfo.info.fingerprint:
                # TODO: staleness?
                break
        else:
            self._remotePeers.append(remotePeerInfo)
            self.remotePeersChanged.emit()

    @Slot(RemotePeerInfo)
    def _onRemotePeerAnnounced(self, remotePeerInfo: RemotePeerInfo):
        self._httpPeer.register(remotePeerInfo, self._info)
        self._onRemotePeerRegistered(remotePeerInfo)
