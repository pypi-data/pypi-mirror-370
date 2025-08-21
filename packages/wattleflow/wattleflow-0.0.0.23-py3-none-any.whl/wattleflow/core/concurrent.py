# Module Name: concurrent.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2025 WattleFlow
# License: Apache 2 License
# Description: This modul contains concurrent pattern interfaces.

"""
This module contains all Wattleflow behavioural interfaces.

Concurrency Interfaces
    Actor-System
        IActor
        ISystem
    Future/Promise
        IFuture
        IPromise
    Callback:
        ICallback
    Reactive Programming
        IObservableReactive
        IObserverReactive
    EventLoop
        IEventLoop
    Pub-Sub (Publisher-Subscriber)
        IPublisher
        ISubscriber
    MessageQueue
        IMessageQueue
    ThreadPool
        IThreadPool
    Coroutine
        ICoroutine
    MapReduce
        IMapper
        IReducer
    Bulk Synchronous Parallel Interfaces
        ISuperstep
        IBSPSystem
    Fork/Join Interfaces
        IForkJoinTask
        IForkJoinPool
    Barier
        IBarrier
    Divide-and-conquer
        IDivideAndConquer
    Data Parallel Task
        IDataParallelTask
    Work-Stealing
        IWorkStealingScheduler
        IWorker
    Stencil
        IStencil
    Graph-Processing
        IGraphProcessing
    SPMD (Single Program, Multiple Data)
        ISPMDProgram
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from threading import Lock
from typing import Any, Callable, Iterable, List, Optional, Generic, TypeVar, Tuple
from .framework import IWattleflow, T

V = TypeVar("V")
Msg = TypeVar("Msg")
Graph = TypeVar("Graph")


# IActor (IActor, ISystem) - Actor-System
class IActor(IWattleflow, ABC, Generic[Msg]):
    @abstractmethod
    def receive(self, message: Msg) -> None: ...


class ISystem(IWattleflow, ABC, Generic[Msg]):
    @abstractmethod
    def create_actor(self, actor_class: type[IActor[Msg]], *args, **kwargs) -> IActor[Msg]: ...

    @abstractmethod
    def send_message(self, actor: IActor[Msg], message: Msg, *args, **kwargs) -> None: ...


# IFuture -(IFuture, IPromise) - Future/Promise interfaces
class IFuture(IWattleflow, ABC, Generic[T]):
    @abstractmethod
    def result(self, timeout: Optional[float] = None) -> T: ...


class IPromise(IWattleflow, ABC, Generic[T]):
    @abstractmethod
    def set_result(self, result: T) -> None: ...


# Callback Interface
class ICallback(IWattleflow, ABC, Generic[T]):
    @abstractmethod
    def call(self, *args, **kwargs) -> T: ...


# IObserverReactive - (IObserverReactive, IObservableReactive) - Reactive Programming Interfaces
class IObserverReactive(IWattleflow, ABC):
    @abstractmethod
    def update(self, observable: "IObservableReactive", *args, **kwargs) -> None: ...


class IObservableReactive(IWattleflow, ABC):
    def __init__(self) -> None:
        super().__init__()
        self._observers: List[IObserverReactive] = []
        self._lock = Lock()

    def add_observer(self, observer: IObserverReactive) -> None:
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def remove_observer(self, observer: IObserverReactive) -> None:
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)

    def notify_observers(self, *args, **kwargs) -> None:
        with self._lock:
            observers_snapshot = list(self._observers)
        for observer in observers_snapshot:
            observer.update(self, *args, **kwargs)


# IEventLoop (IEventLoop) Event-Loop Interface
class IEventLoop(IWattleflow, ABC):
    @abstractmethod
    def run_forever(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def call_soon(self, callback: Callable[..., None], *args) -> None: ...


# IPublisher - (IPublisher-ISubscriber) - Pub-Sub interface
class IPublisher(IWattleflow, ABC, Generic[Msg]):
    @abstractmethod
    def subscribe(self, subscriber: "ISubscriber[Msg]") -> None: ...

    @abstractmethod
    def unsubscribe(self, subscriber: "ISubscriber[Msg]") -> None: ...

    @abstractmethod
    def notify(self, message: Msg) -> None: ...


class ISubscriber(IWattleflow, ABC, Generic[Msg]):
    @abstractmethod
    def update(self, message: Msg) -> None: ...


# Message-Que Interface
class IMessageQueue(IWattleflow, ABC, Generic[Msg]):
    @abstractmethod
    def send(self, message: Msg) -> None: ...

    @abstractmethod
    def receive(self, timeout: Optional[float] = None) -> Optional[Msg]: ...


# ThreadPool-Pool Interface
class IThreadPool(IWattleflow, ABC):
    @abstractmethod
    def submit(self, task: Callable[..., T], *args, **kwargs) -> IFuture[T]: ...

    @abstractmethod
    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None: ...


# Coroutine Interface
class ICoroutine(IWattleflow, ABC, Generic[T]):
    @abstractmethod
    def send(self, value: T) -> T: ...

    @abstractmethod
    def throw(self, typ: type[BaseException], val: BaseException | None = None, tb=None) -> T: ...

    @abstractmethod
    def close(self) -> None: ...


# MapReduce Interface (IMapper, IReducer)
class IMapper(IWattleflow, ABC, Generic[T, V]):
    @abstractmethod
    def map(self, data: Iterable[V]) -> Iterable[Tuple[T, V]]: ...


class IReducer(IWattleflow, ABC, Generic[T, V]):
    @abstractmethod
    def reduce(self, key: T, values: Iterable[V]) -> Tuple[T, V]: ...


# ISuperstep - (ISuperstep, IBSPSystem) - Bulk Synchronous Parallel interfaces
class ISuperstep(IWattleflow, ABC):
    @abstractmethod
    def execute(self, data: Any) -> Any: ...


class IBSPSystem(IWattleflow, ABC):
    @abstractmethod
    def run_supersteps(self, supersteps, data) -> None: ...


# IForkJoinTask (IForkJoinTask, IForkJoinPool) - Fork/Join interfaces
class IForkJoinTask(IWattleflow, ABC):
    @abstractmethod
    def fork(self) -> None: ...

    @abstractmethod
    def join(self) -> None: ...


class IForkJoinPool(IWattleflow, ABC):
    @abstractmethod
    def invoke(self, task: Any) -> None: ...


# IBarrier - Barier Interface
class IBarrier(IWattleflow, ABC):
    @abstractmethod
    def wait(self) -> None: ...


# IDivideAndConquer
class IDivideAndConquer(IWattleflow, ABC):
    @abstractmethod
    def divide(self, problem: Any) -> None: ...

    @abstractmethod
    def solve_subproblem(self, subproblem: Any) -> None: ...

    @abstractmethod
    def combine(self, solutions: Any) -> None: ...


# IDataParallelTask
class IDataParallelTask(IWattleflow, ABC):
    @abstractmethod
    def execute(self, data_chunk: Any) -> None: ...


# IWorkStealingScheduler -(IWorkStealingScheduler, IWorker) - Work-Stealing interface
class IWorkStealingScheduler(IWattleflow, ABC):
    @abstractmethod
    def steal(self) -> None: ...


class IWorker(IWattleflow, ABC):
    @abstractmethod
    def do_work(self) -> None: ...


# IStencil
class IStencil(IWattleflow, ABC):
    @abstractmethod
    def apply(self, grid, point) -> None: ...


# IGraphProcessing
class IGraphProcessing(IWattleflow, Generic[Graph], ABC):
    @abstractmethod
    def process_vertex(self, vertex: Graph) -> None: ...

    @abstractmethod
    def process_edge(self, edge: Graph) -> None: ...


# ISPMDProgram - Single Program, Multiple Data
class ISPMDProgram(IWattleflow, ABC):
    @abstractmethod
    def execute(self, data_partition: Any) -> None: ...
