from typing import TYPE_CHECKING

from PySide6.QtCore import Property
from PySide6.QtQml import QmlElement, QmlSingleton


def _id[T](x: T):
    return x


def _FakeProperty(*args, **kwargs):
    return property


if TYPE_CHECKING:
    Property = _FakeProperty
    QmlElement = _id
    QmlSingleton = _id
