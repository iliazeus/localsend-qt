from dataclasses import asdict
import json
import sys

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtNetwork import QHostAddress, QNetworkInterface, QUdpSocket

from .dto import AnnouncementDto
from .peer_info import PeerInfo
from .remote_peer_info import RemotePeerInfo


class UdpPeer(QObject):
    PORT = 53317
    MULTICAST_ADDRESS = QHostAddress("224.0.0.167")

    _info: PeerInfo
    _socket: QUdpSocket
    _announceTimer: QTimer | None = None

    remotePeerAnnounced = Signal(RemotePeerInfo)

    def __init__(
        self,
        parent: QObject | None = None,
        *,
        info: PeerInfo,
        announceIntervalMs: int | None = 10_000,
    ):
        super().__init__(parent)

        self._info = info

        self._socket = QUdpSocket(self)
        assert self._socket.bind(
            QHostAddress.SpecialAddress.AnyIPv4,
            self.PORT,
            mode=QUdpSocket.BindFlag.ReuseAddressHint,
        )
        self._socket.readyRead.connect(self._onSocketReadyRead)

        self._announce()

        if announceIntervalMs is not None:
            self._announceTimer = QTimer(self)
            self._announceTimer.setInterval(announceIntervalMs)
            self._announceTimer.timeout.connect(self._announce)
            self._announceTimer.start()

    @Slot()
    def _announce(self):
        payload = self._info.makeAnnouncement()
        payload = json.dumps(asdict(payload)).encode()

        for iface in QNetworkInterface.allInterfaces():
            if len(iface.addressEntries()) > 0:
                self._socket.joinMulticastGroup(self.MULTICAST_ADDRESS, iface)

        print(f"trying to announce", file=sys.stderr)

        ret = self._socket.writeDatagram(
            payload,
            self.MULTICAST_ADDRESS,
            self.PORT,
        )
        assert ret > 0

    @Slot()
    def _onSocketReadyRead(self):
        dgram = self._socket.receiveDatagram()
        assert dgram.isValid()

        payload = json.loads(dgram.data().toStdString())
        payload = AnnouncementDto(**payload)

        if payload.fingerprint == self._info.fingerprint:
            return

        print(f"received announcement from {payload.alias}")

        remotePeerInfo = RemotePeerInfo(
            address=dgram.senderAddress(),
            info=PeerInfo.fromAnnouncement(payload),
        )

        self.remotePeerAnnounced.emit(remotePeerInfo)
