from typing import Literal

from pydantic.dataclasses import dataclass

type DeviceType = Literal["mobile", "desktop", "web", "headless", "server"]


@dataclass
class AnnouncementDto:
    alias: str
    version: str
    fingerprint: str
    port: int
    protocol: Literal["http", "https"]
    deviceModel: str | None = None
    deviceType: DeviceType | None = None
    download: bool = False
    announce: bool = False
