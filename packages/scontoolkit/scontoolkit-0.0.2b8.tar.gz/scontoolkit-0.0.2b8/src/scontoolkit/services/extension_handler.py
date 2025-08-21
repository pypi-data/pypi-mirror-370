
from collections import defaultdict
from typing import Any, Type, List
import importlib.metadata

class ExtensionRegistry:
    _plugins: List = []
    _srv_by_interface: defaultdict[type, list] = defaultdict(list)
    def __init__(self):
        entry_points = importlib.metadata.entry_points()
        eps = entry_points.select(group="sconext")
        print(eps)

        for ep in eps:
            cls = ep.load()  # Load the class
            instance = cls()
            self.__register_service__(instance)


    @classmethod
    def __register_service__(cls, instance: Any):
        for base in type(instance).__mro__:
            if base.__module__.startswith("scontoolkit.interfaces."):
                cls._srv_by_interface[base].append(instance)

    @classmethod
    def get_by_interface(cls, interface: Type) -> list[Any]:
        return cls._srv_by_interface.get(interface, [])
