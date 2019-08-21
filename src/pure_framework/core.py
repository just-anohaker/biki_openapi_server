from typing import Union
from src.pure_framework.interfaces import IModel, IProxy, IController, IMediator


class Model(IModel):
    def __init__(self):
        self._proxies = dict()

        self._init_model()

    def _init_model(self) -> None:
        pass

    def register_proxy(self, proxy: IProxy) -> None:
        if self.has_proxy(proxy.get_proxy_name()):
            return

        self._proxies[proxy.get_proxy_name()] = proxy
        proxy.on_register()

    def remove_proxy(self, proxy_name: str) -> Union[IProxy, None]:
        if not self.has_proxy(proxy_name):
            return None

        find_proxy = self._proxies.get(proxy_name)
        del self._proxies[proxy_name]
        find_proxy.on_remove()
        return find_proxy

    def retrieve_proxy(self, proxy_name: str) -> Union[IProxy, None]:
        if not self.has_proxy(proxy_name):
            return None

        find_proxy = self._proxies.get(proxy_name)
        return find_proxy

    def has_proxy(self, proxy_name: str) -> bool:
        return self._proxies.get(proxy_name) is not None


class Controller(IController):
    def __init__(self):
        self._mediators = dict()
        self._init_controller()

    def _init_controller(self) -> None:
        pass

    def register_mediator(self, mediator: IMediator) -> None:
        if self.has_mediator(mediator.get_mediator_name()):
            return

        self._mediators[mediator.get_mediator_name()] = mediator
        mediator.on_register()

    def remove_mediator(self, mediator_name: str) -> Union[IMediator, None]:
        if not self.has_mediator(mediator_name):
            return None

        find_mediator = self._mediators.get(mediator_name)
        del self._mediators[mediator_name]
        find_mediator.on_remove()
        return find_mediator

    def retrieve_mediator(self, mediator_name: str) -> Union[IMediator, None]:
        if not self.has_mediator(mediator_name):
            return None

        find_mediator = self._mediators.get(mediator_name)
        return find_mediator

    def has_mediator(self, mediator_name: str) -> bool:
        return self._mediators.get(mediator_name) is not None
