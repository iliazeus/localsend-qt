import copy
import secrets


from PySide6.QtCore import QObject, QTimer, Signal, Slot

from names_generator import generate_name


from peer.common import *
from peer import http, udp


class Peer(QObject):
    instance: Peer = None  # type: ignore

    _info: PeerInfo
    _remote_peers: dict[str, RemotePeer]

    _http_peer: http.HttpPeer
    _udp_peer: udp.UdpPeer

    _announce_timer: QTimer

    def get_info(self) -> PeerInfo:
        return copy.deepcopy(self._info)

    def get_remote_peers(self) -> dict[str, RemotePeer]:
        return copy.deepcopy(self._remote_peers)

    remote_peers_changed = Signal()

    def __init__(
        self,
        parent: QObject | None = None,
    ):
        super().__init__(parent)

        assert Peer.instance is None
        Peer.instance = self

        self._info = PeerInfo(
            version="2.0",
            alias=generate_name(style="capital"),
            fingerprint=secrets.token_urlsafe(),
            protocol="http",
            port=PORT,
            announce=True,
            deviceType="desktop",
        )

        self._remote_peers = {}

        self._http_peer = http.HttpPeer(self)
        self._http_peer.remote_peer_registered.connect(self._on_remote_peer_registered)

        self._udp_peer = udp.UdpPeer(self)
        self._udp_peer.remote_peer_announced.connect(self._on_remote_peer_announced)

        self._announce_timer = QTimer(self)
        self._announce_timer.setInterval(10_000)
        self._announce_timer.timeout.connect(self._announce)
        self._announce_timer.start()

        self._announce()

    @Slot()
    def _announce(self):
        stale_peer_fingerprints = []
        for peer in self._remote_peers.values():
            peer.staleness += self._announce_timer.interval()
            if peer.staleness > 30_000:
                stale_peer_fingerprints.append(peer.info.fingerprint)
        for fingerprint in stale_peer_fingerprints:
            del self._remote_peers[fingerprint]
        if len(stale_peer_fingerprints) > 0:
            self.remote_peers_changed.emit()

        self._udp_peer.announce(self._info)

    @Slot(object)
    def _on_remote_peer_announced(self, peer: RemotePeer):
        self._http_peer.register(peer, self._info)
        self._register_peer(peer)

    @Slot(object)
    def _on_remote_peer_registered(self, peer: RemotePeer):
        self._register_peer(peer)

    def _register_peer(self, peer: RemotePeer):
        if (
            peer.info.fingerprint not in self._remote_peers
            and peer.info.fingerprint != self._info.fingerprint
        ):
            self._remote_peers[peer.info.fingerprint] = peer
            self.remote_peers_changed.emit()
