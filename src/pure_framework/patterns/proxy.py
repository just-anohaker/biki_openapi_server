from src.pure_framework.interfaces import IProxy, INotifier, IFacade
from src.pure_framework.patterns.observer import Notifier


class Proxy(Notifier, IProxy, INotifier):
    NAME = "Proxy"

    def __init__(self, name: str, facade: IFacade):
        self._facade = facade
        proxy_name = name or self.NAME
        if proxy_name is None:
            raise ValueError("Proxy name cannot be None")

        self._proxy_name = proxy_name

    def get_proxy_name(self) -> str:
        return self._proxy_name

    def on_register(self) -> None:
        pass

    def on_remove(self) -> None:
        pass
