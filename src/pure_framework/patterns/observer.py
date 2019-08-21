from typing import Callable
from src.pure_framework.interfaces import IObserver, INotifier, INotification, IFacade


class Observer(IObserver):
    def __init__(self, method: Callable[[INotification], None], context: object):
        self._method = None
        self._context = None

        self.set_notify_method(method)
        self.set_notify_context(context)

    def set_notify_method(self, notify_method: Callable[[INotification], None]) -> None:
        self._method = notify_method

    def set_notify_context(self, notify_context: object) -> None:
        self._context = notify_context

    def get_notify_method(self) -> Callable:
        return self._method

    def get_notify_context(self) -> object:
        return self._context

    def notify_observer(self, notification: INotification) -> None:
        self._method(notification)

    def compare_notify_context(self, obj: object) -> bool:
        return obj is self._context


class Notifier(INotifier):
    def __init(self, facade: IFacade):
        self._facade = facade

    def send_notification(self, notification_name: str, body: object = None, note_type: str = None) -> None:
        self._facade.send_notification(notification_name, body, note_type)


class Notification(INotification):
    def __init__(self, name: str, body: object = None, note_type: str = None):
        self._name = name
        self._body = body
        self._type = note_type

    def get_name(self) -> str:
        return self._name

    def set_body(self, body: object) -> None:
        self._body = body

    def get_body(self) -> object:
        return self._body

    def set_type(self, note_type: str) -> None:
        self._type = note_type

    def get_type(self) -> str:
        return self._type

    def str(self) -> str:
        msg = "Notification Name:" + self.get_name()

        bd = "None"
        if self._body is not None:
            bd = str(self._body)

        ty = "None"
        if self._type is not None:
            ty = str(self._type)

        msg += "\nBody:" + bd
        msg += "\nType:" + ty
        return msg
