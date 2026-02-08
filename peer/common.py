from typing import Literal

from PySide6.QtNetwork import QHostAddress


from pydantic.dataclasses import dataclass


MULTICAST_ADDRESS = QHostAddress("224.0.0.167")
PORT = 53317


type DeviceType = Literal["mobile", "desktop", "web", "headless", "server"]


@dataclass
class PeerInfo:
    alias: str
    version: str
    fingerprint: str
    port: int
    protocol: Literal["http", "https"]
    deviceModel: str | None = None
    deviceType: DeviceType | None = None
    download: bool = False
    announce: bool = False


@dataclass
class RemotePeer:
    address: str
    info: PeerInfo
    staleness: int = 0
