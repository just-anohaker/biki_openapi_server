from typing import Union
from src.pure_framework.interfaces import IFacade, INotifier, IProxy, IMediator, IObserver, INotification
from src.pure_framework.core import Controller, Model
from src.pure_framework.patterns.observer import Notifier, Notification


class Facade(Notifier, IFacade, INotifier):
    def __init__(self):
        self._observers = dict()
        self._model = None
        self._controller = None
        self._init_facade()

    def _init_facade(self) -> None:
        self._initialize_model()
        self._initialize_controller()

    def _initialize_model(self):
        if self._model is None:
            self._model = Model()

    def _initialize_controller(self):
        if self._controller is None:
            self._controller = Controller()

    def register_proxy(self, proxy: IProxy) -> None:
        self._model.register_proxy(proxy)

    def remove_proxy(self, proxy_name: str) -> Union[IProxy, None]:
        return self._model.remove_proxy(proxy_name)

    def retrieve_proxy(self, proxy_name: str) -> Union[IProxy, None]:
        return self._model.retrieve_proxy(proxy_name)

    def has_proxy(self, proxy_name: str) -> bool:
        return self._model.has_proxy(proxy_name)

    def register_mediator(self, mediator: IMediator) -> None:
        self._controller.register_mediator(mediator)

    def remove_mediator(self, mediator_name: str) -> Union[IMediator, None]:
        return self._controller.remove_mediator(mediator_name)

    def retrieve_mediator(self, mediator_name: str) -> Union[IMediator, None]:
        return self._controller.retrieve_mediator(mediator_name)

    def has_mediator(self, mediator_name: str) -> bool:
        return self._controller.has_mediator(mediator_name)

    def register_observer(self, notification_name: str, observer: IObserver) -> None:
        observers = self._observers.get(notification_name)
        if observers is None:
            observers = [observer]
        else:
            observers.append(observer)
        self._observers[notification_name] = observers

    def remove_observer(self, notification_name: str, context: object) -> None:
        observers = self._observers.get(notification_name)
        if observers is None:
            return
        for observer in observers:
            if observer.compare_notify_context(context):
                observers.remove(observer)
                break

        if len(observers) <= 0:
            del self._observers[notification_name]
        else:
            self._observers[notification_name] = observers

    def notify_observer(self, notification: INotification) -> None:
        name = notification.get_name()
        observers = self._observers.get(name)
        if observers is not None:
            cp_observers = observers[:]
            for observer in cp_observers:
                observer.notify_observer(notification)

    def send_notification(self, notification_name: str, body: object = None, note_type: str = None) -> None:
        self.notify_observer(Notification(notification_name, body, note_type))
