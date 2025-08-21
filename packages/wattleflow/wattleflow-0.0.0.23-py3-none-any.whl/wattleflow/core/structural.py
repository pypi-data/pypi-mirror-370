# Module Name: structural.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2025 WattleFlow
# License: Apache 2 License
# Description: This modul contains structural pattern interfaces.

"""
This module contains all Wattleflow structural interfaces.

Structural interfaces
    Adapter
        ITarget
        IAdaptee
        IAdapter
    Bridge
        IImplementor
        IAbstraction
    Composite
        IComponent
        IComposite
    Decorator
        IDecorator
    Facade
        IFacade
    Flyweight
        IFlyweight
        IFlyweightFactory
    Proxy
        IProxy
"""

from abc import abstractmethod, ABC
from typing import Any, Generic
from .framework import IWattleflow, T


# IAdaptee (IAdaptee, IAdapter, ITarget) - Adapter interfaces
class IAdaptee(IWattleflow, ABC):
    def specific_request(self) -> "IAdaptee":
        return self


class ITarget(IWattleflow, ABC):
    @abstractmethod
    def request(self) -> IAdaptee: ...


class IAdapter(IWattleflow, ABC):
    def __init__(self, adaptee: IAdaptee):
        super().__init__()
        self._adaptee = adaptee


# IImplementor (IImplementor, IAbstraction) - Bridge interfaces
class IImplementor(IWattleflow, ABC):
    @abstractmethod
    def operation_impl(self) -> None: ...


class IAbstraction(IWattleflow, ABC):
    @abstractmethod
    def operation(self) -> None: ...


# ICompoenent (IComponent, IComposite) - Composite interface
class IComponent(IWattleflow, Generic[T], ABC):
    @abstractmethod
    def process(self, data: T) -> None: ...


class IComposite(IComponent, ABC):
    @abstractmethod
    def add(self, component: IComponent) -> None: ...

    @abstractmethod
    def remove(self, component: IComponent): ...

    @abstractmethod
    def get_child(self, index) -> IComponent: ...


# IDecorator
class IDecorator(IComponent, ABC):
    @abstractmethod
    def set_component(self, component: IComponent) -> None: ...


# IFacade
class IFacade(IWattleflow, ABC):
    @abstractmethod
    def operation(self, action: int) -> bool: ...


# IFlyweight (IFlyweight, IFlyweightFactory)
class IFlyweight(IWattleflow, Generic[T], ABC):
    @abstractmethod
    def operation(self, extrinsic_state: T) -> None: ...


class IFlyweightFactory(IWattleflow, ABC):
    @abstractmethod
    def get_flyweight(self, key: str) -> Any: ...


# Proxy interface
class IProxy(IWattleflow, ABC):
    @abstractmethod
    def request(self) -> Any: ...
