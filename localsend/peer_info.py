from typing import Literal, Self, TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from .dto import AnnouncementDto, DeviceType
from .util import Property, QmlElement


QML_IMPORT_NAME = "lol.iliazeus.localsend"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PeerInfo(QObject):
    _alias: str
    _version: str
    _fingerprint: str
    _port: int
    _protocol: Literal["http", "https"]
    _deviceModel: str | None = None
    _deviceType: DeviceType | None = None
    _download: bool = False

    @Property(str, constant=True)
    def alias(self) -> str:
        return self._alias

    @Property(str, constant=True)
    def version(self) -> str:
        return self._version

    @Property(str, constant=True)
    def fingerprint(self) -> str:
        return self._fingerprint

    @Property(int, constant=True)
    def port(self) -> int:
        return self._port

    @Property(str, constant=True)
    def protocol(self) -> Literal["http", "https"]:
        return self._protocol

    @Property(str, constant=True)
    def deviceModel(self) -> str | None:
        return self._deviceModel

    @Property(str, constant=True)
    def deviceType(self) -> DeviceType | None:
        return self._deviceType

    @Property(bool, constant=True)
    def download(self) -> bool:
        return self._download

    def __init__(
        self,
        parent: QObject | None = None,
        *,
        alias: str,
        version: str,
        fingerprint: str,
        port: int,
        protocol: Literal["http", "https"],
        deviceModel: str | None = None,
        deviceType: DeviceType | None = None,
        download: bool = False,
    ):
        super().__init__(parent)
        self._alias = alias
        self._version = version
        self._fingerprint = fingerprint
        self._port = port
        self._protocol = protocol
        self._deviceModel = deviceModel
        self._deviceType = deviceType
        self._download = download

    def makeAnnouncement(self) -> AnnouncementDto:
        return AnnouncementDto(
            alias=self._alias,
            version=self._version,
            fingerprint=self._fingerprint,
            port=self._port,
            protocol=self._protocol,
            deviceModel=self._deviceModel,
            deviceType=self._deviceType,
            download=self._download,
            announce=True,
        )

    @classmethod
    def fromAnnouncement(
        cls,
        dto: AnnouncementDto,
        parent: QObject | None = None,
    ) -> Self:
        return cls(
            parent=parent,
            alias=dto.alias,
            version=dto.version,
            fingerprint=dto.fingerprint,
            port=dto.port,
            protocol=dto.protocol,
            deviceModel=dto.deviceModel,
            deviceType=dto.deviceType,
            download=dto.download,
        )
