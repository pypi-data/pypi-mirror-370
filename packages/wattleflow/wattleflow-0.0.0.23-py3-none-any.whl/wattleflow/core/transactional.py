# Module Name: transactional.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2025 WattleFlow
# License: Apache 2 License
# Description: This modul contains transactional pattern interfaces.

"""
This module contains all Wattleflow transactional interfaces.

Additional Interfaces Specific to Flow-Based Programming
    Blackboard
        IBlackboard
    Event-Driven
        IEventListener
        IEventSource
    Pipeline
        IPipeline
    Query
        IQuery
    Repository
        IRepository
    Saga
        ISaga
    Unit-of-work
        IUnitOfWork
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import (
    Any,
    Dict,
    Generic,
    Optional,
)
from .framework import T
from .framework import IWattleflow
from .creational import ISingleton
from .structural import IAdaptee, ITarget


# Document
class IDocument(IAdaptee, Generic[T], ABC):

    @property
    @abstractmethod
    def identifier(self) -> str: ...

    @abstractmethod
    def update_content(self, content: T): ...

    @abstractmethod
    def specific_request(self) -> T: ...


# Signal
class ISignal(IAdaptee, Generic[T], ABC):
    __slots__ = ("_identifier", "_signal", "_timestamp")

    @property
    @abstractmethod
    def identifier(self) -> str: ...

    @abstractmethod
    def specific_request(self) -> T: ...


# IEvent - (IEvent, IEventListener, IDataflowComponent) - Event-Driven
class IEvent(ABC):
    @property
    @abstractmethod
    def correlation_id(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def source(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def timestamp(self) -> datetime: ...

    @property
    @abstractmethod
    def type(self) -> str: ...

    @property
    @abstractmethod
    def payload(self) -> Dict[str, Any]: ...


class IEventListener(IWattleflow, ABC):
    @abstractmethod
    def on_event(self, event: IEvent) -> None: ...


class IEventSource(IWattleflow, ABC):
    @abstractmethod
    def register_listener(self, listener: IEventListener) -> None: ...

    @abstractmethod
    def emit_event(self, event: Any) -> None: ...


# IRepository
class IRepository(IWattleflow, ABC):
    @property
    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def clear(self) -> None: ...

    @abstractmethod
    def read(self, identifier: str, *args, **kwargs) -> ITarget: ...

    @abstractmethod
    def write(self, document: ITarget, *args, **kwargs) -> bool: ...


# IBlackboard - (IBlackboard, IModule)
class IBlackboard(IWattleflow, ABC):
    @property
    @abstractmethod
    def canvas(self) -> Dict[str, Any]: ...

    @property
    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def clear(self) -> None: ...

    @abstractmethod
    def create(self, caller: IWattleflow, *args, **kwargs) -> ITarget: ...

    @abstractmethod
    def read(self, identifier: str) -> ITarget: ...

    @abstractmethod
    def register(self, repository: IRepository): ...

    @abstractmethod
    def write(
        self,
        caller: IWattleflow,
        document: ITarget,
        *args,
        **kwargs,
    ) -> str: ...


class IModule(IWattleflow, ABC):
    @abstractmethod
    def update(self, blackboard: IBlackboard, *args, **kwargs) -> None: ...


# IPipeline
class IPipeline(IWattleflow, ABC):
    @abstractmethod
    def process(
        self,
        processor: "IProcessor",
        document: ITarget,
        *args,
        **kwargs,
    ) -> None: ...


# IProcessor
class IProcessor(IWattleflow, Generic[T], ABC):
    @abstractmethod
    def create_generator(self) -> T: ...

    @abstractmethod
    def start(self) -> None: ...


# IQuery
class IQuery(IWattleflow, Generic[T], ABC):
    @abstractmethod
    def execute(self) -> T: ...


# Saga pattern
class ISaga(IWattleflow, Generic[T], ABC):
    @abstractmethod
    def start(self, initial_state, *args, **kwargs) -> None: ...

    @abstractmethod
    def handle_event(self, event: T, *args, **kwargs) -> None: ...

    @abstractmethod
    def compensate(self) -> None: ...


# IUnitOfWork
class IUnitOfWork(IWattleflow, Generic[T], ABC):
    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    @abstractmethod
    def register_new(self, entity: T, *args, **kwargs) -> None: ...

    @abstractmethod
    def register_dirty(self, entity: T, *args, **kwargs) -> None: ...

    @abstractmethod
    def register_deleted(self, entity: T, *args, **kwargs) -> None: ...


# IScheduler
class IScheduler(ISingleton, Generic[T], IEventSource):
    @abstractmethod
    def setup_orchestrator(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def start_orchestration(self, parallel: bool) -> None: ...

    @abstractmethod
    def stop_orchestration(self) -> None: ...

    @abstractmethod
    def register_listener(self, listener: IEventListener) -> None: ...

    @abstractmethod
    def emit_event(self, event: T, **kwargs) -> None: ...
