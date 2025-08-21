# Module Name: core/abstract/behavioural.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2025 WattleFlow
# License: Apache 2 License
# Description: This modul contains creational pattern interfaces.

"""
This module contains all Wattleflow creational interfaces.

Creational Interfaces
    Abstract Factory
        IFactory
    Builder
        IBuilder
    Factory Method
        ICreator
        IProduct
    Prototype
        IPrototype
    Singleton
        ISingleton
"""


import inspect
from abc import abstractmethod, ABC
from .framework import IWattleflow


# Creational design patterns
# Abstract Factory Interface
class IFactory(IWattleflow, ABC):
    @staticmethod
    def create():
        pass


# Builder
class IBuilder(IWattleflow, ABC):
    """
    def make_part_a(self)
    def make_part_b(self)
    def build(self)
        a = self.make_part_a()
        b = self.make_part_b()
        return a + b
    """

    # @abstractmethod
    # def build_part(self):
    #     pass
    @abstractmethod
    def build(self):
        pass


# Factory Method Interface (ICreator, IProduct)
class IProduct(IWattleflow, ABC):
    @abstractmethod
    def operation(self):
        pass


class ICreator(IWattleflow, ABC):
    @abstractmethod
    def factory_method(self):
        pass


# Prototype Interface
class IPrototype(IWattleflow, ABC):
    @abstractmethod
    def clone(self):
        pass


# Singleton Interface
class ISingleton(IWattleflow):
    import threading  # pylint: disable=import-outside-toplevel

    _lock = threading.Lock()
    _instances = {}

    @abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        # if class is apstract, don't cache
        if inspect.isabstract(cls):
            return super().__new__(cls)

        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]