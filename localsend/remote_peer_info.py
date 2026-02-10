from PySide6.QtCore import QObject, QUrl
from PySide6.QtNetwork import QHostAddress

from .peer_info import PeerInfo
from .util import Property, QmlElement


QML_IMPORT_NAME = "lol.iliazeus.localsend"
QML_IMPORT_MAJOR_VERSION = 1


def _wrapIpv6(s: str) -> str:
    if ":" in s:
        return "[" + s + "]"
    else:
        return s


@QmlElement
class RemotePeerInfo(QObject):
    _address: QHostAddress
    _info: PeerInfo

    @Property(QHostAddress)
    def address(self) -> QHostAddress:
        return self._address

    @Property(PeerInfo)
    def info(self) -> PeerInfo:
        return self._info

    @Property(QUrl)
    def url(self) -> QUrl:
        url = QUrl()
        url.setScheme(self._info.protocol)
        url.setHost(_wrapIpv6(self._address.toString()))
        url.setPort(self._info.port)
        return url

    def __init__(
        self,
        parent: QObject | None = None,
        *,
        address: QHostAddress,
        info: PeerInfo,
    ):
        super().__init__(parent)

        self._address = address
        self._info = info

        self._info.setParent(self)
