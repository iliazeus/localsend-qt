import sys

from PySide6.QtCore import Slot
from PySide6.QtNetwork import QHostAddress

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from names_generator import generate_name
from pydantic.dataclasses import dataclass


from peer import Peer, RemotePeer


class MainWindow(QWidget):
    _peer: Peer

    _remote_peer_list: QListWidget

    def __init__(self):
        super().__init__()

        self._peer = Peer(self)
        self._peer.remote_peers_changed.connect(self._on_remote_peers_changed)

        peer_info = self._peer.get_info()

        self.resize(400, 500)

        self.setWindowTitle(f"QLocalSend: {peer_info.alias}")

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel(f"<center><big>{peer_info.alias}</big></center>"))
        layout.addWidget(QLabel(f"Peers:"))

        self._remote_peer_list = QListWidget()
        layout.addWidget(self._remote_peer_list)

        self._remote_peer_list_items = {}

    @Slot()
    def _on_remote_peers_changed(self):
        peers = self._peer.get_remote_peers()
        for fingerprint in self._remote_peer_list_items:
            if fingerprint not in peers:
                item = self._remote_peer_list_items[fingerprint]
                self._remote_peer_list.takeItem(self._remote_peer_list.row(item))
        for fingerprint in peers:
            if fingerprint not in self._remote_peer_list_items:
                peer = peers[fingerprint]
                item = QListWidgetItem()
                item.setText(f"{peer.info.alias} ({peer.address})")
                self._remote_peer_list.addItem(item)
                self._remote_peer_list_items[fingerprint] = item


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
