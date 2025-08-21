# Module Name: core/abstract/framework.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2025 WattleFlow
# License: Apache 2 License
# Description: This modul contains framework pattern interfaces.


from abc import ABC
from typing import TypeVar


class IWattleflow(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.name = self.__class__.__name__

    # def __getattr__(self, name: str) -> Optional[object]:
    #     d = getattr(self, "__dict__", None)
    #     if d is not None and name in d:
    #         return d[name]
    #     return None


T = TypeVar("T")
W = TypeVar("W", bound=IWattleflow)
