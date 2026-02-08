from dataclasses import asdict
import json

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtNetwork import QHostAddress, QNetworkInterface, QUdpSocket

from peer.common import *


class UdpPeer(QObject):
    _socket: QUdpSocket

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self._socket = QUdpSocket(self)
        self._socket.readyRead.connect(self._on_socket_ready_read)
        assert self._socket.bind(
            QHostAddress.SpecialAddress.AnyIPv4,
            PORT,
            QUdpSocket.BindFlag.ReuseAddressHint,
        )
        for iface in QNetworkInterface.allInterfaces():
            if len(iface.addressEntries()) > 0:
                assert self._socket.joinMulticastGroup(MULTICAST_ADDRESS, iface)

    remote_peer_announced = Signal(object)  # RemotePeer

    def announce(self, info: PeerInfo):
        ret = self._socket.writeDatagram(
            json.dumps(asdict(info)).encode(),
            MULTICAST_ADDRESS,
            PORT,
        )
        assert ret > 0

    @Slot()
    def _on_socket_ready_read(self):
        dgram = self._socket.receiveDatagram()
        assert dgram.isValid()

        peer = RemotePeer(
            dgram.senderAddress().toString(),
            PeerInfo(**json.loads(dgram.data().toStdString())),
        )
        self.remote_peer_announced.emit(peer)
