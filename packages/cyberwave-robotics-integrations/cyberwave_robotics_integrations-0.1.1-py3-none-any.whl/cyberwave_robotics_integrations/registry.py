from __future__ import annotations

from typing import List, Type

from .base_robot import BaseRobot


DRIVER_CLASSES: List[Type[BaseRobot]] = []


def register(driver_cls: Type[BaseRobot]):
    DRIVER_CLASSES.append(driver_cls)
    return driver_cls


