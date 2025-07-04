import importlib
from typing import Callable, Dict, Type

from scheduler.base_scheduler import BaseScheduler


class SchedulerFactory:
    _registry: Dict[str, Callable[[], Type[BaseScheduler]]] = {}

    @classmethod
    def register_scheduler(cls, name: str, module_path: str, class_name: str) -> None:
        """Register a connector with a lazy-loading module and class name."""
        if name in cls._registry:
            raise ValueError(f"Connector '{name}' is already registered.")

        def loader() -> Type[BaseScheduler]:
            module = importlib.import_module(module_path)
            return getattr(module, class_name)

        cls._registry[name] = loader

    @classmethod
    def create_scheduler(cls, scheduler_name: str, prefills, decodes, cpus) -> BaseScheduler:
        if scheduler_name not in cls._registry:
            raise ValueError(f"Unsupported connector type: {scheduler_name}")

        scheduler_cls = cls._registry[scheduler_name]()
        return scheduler_cls(prefills, decodes, cpus)


# Register various connectors here.
# The registration should not be done in each individual file, as we want to
# only load the files corresponding to the current connector.
SchedulerFactory.register_scheduler(
    "Naive",
    "scheduler.naive_scheduler",
    "NaiveScheduler")
