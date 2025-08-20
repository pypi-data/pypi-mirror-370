class ServiceRegistry:
    _services = {}

    @classmethod
    def register(cls, name: str, instance: object):
        if name in cls._services:
            raise ValueError(f"Service '{name}' is already registered.")
        cls._services[name] = instance

    @classmethod
    def get(cls, name: str) -> object:
        return cls._services.get(name)

    @classmethod
    def all(cls) -> dict[str, object]:
        return dict(cls._services)  # return a copy to prevent direct mutation

    @classmethod
    def clear(cls):
        cls._services.clear()
