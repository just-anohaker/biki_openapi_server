from typing import Callable, Union


class INotifier(object):
    def send_notification(self, notification_name: str, body: object = None, note_type: str = None) -> None:
        raise NotImplementedError(self)


class INotification(object):
    def get_name(self) -> str:
        raise NotImplementedError(self)

    def set_body(self, body: object) -> None:
        raise NotImplementedError(self)

    def get_body(self) -> object:
        raise NotImplementedError(self)

    def set_type(self, note_type: str) -> None:
        raise NotImplementedError(self)

    def get_type(self) -> str:
        raise NotImplementedError(self)


class IObserver(object):
    def set_notify_method(self, notify_method: Callable) -> None:
        raise NotImplementedError(self)

    def set_notify_context(self, notify_context: object) -> None:
        raise NotImplementedError(self)

    def get_notify_method(self) -> Callable:
        raise NotImplementedError(self)

    def get_notify_context(self) -> object:
        raise NotImplementedError(self)

    def notify_observer(self, notification: INotification) -> None:
        raise NotImplementedError(self)

    def compare_notify_context(self, obj: object) -> bool:
        raise NotImplementedError(self)


class IProxy(INotifier):
    def get_proxy_name(self) -> str:
        raise NotImplementedError(self)

    def on_register(self) -> None:
        raise NotImplementedError(self)

    def on_remove(self) -> None:
        raise NotImplementedError(self)

    # overwrite
    def send_notification(self, notification_name: str, body: object = None, note_type: str = None) -> None:
        raise NotImplementedError(self)


class IMediator(INotifier):
    def get_mediator_name(self) -> str:
        raise NotImplementedError(self)

    def on_register(self) -> None:
        raise NotImplementedError(self)

    def on_remove(self) -> None:
        raise NotImplementedError(self)

    # overwrite
    def send_notification(self, notification_name: str, body: object = None, note_type: str = None) -> None:
        raise NotImplementedError(self)


class IModel(object):
    def register_proxy(self, proxy: IProxy) -> None:
        raise NotImplementedError(self)

    def retrieve_proxy(self, proxy_name: str) -> Union[IProxy, None]:
        raise NotImplementedError(self)

    def remove_proxy(self, proxy_name: str) -> Union[IProxy, None]:
        raise NotImplementedError(self)

    def has_proxy(self, proxy_name: str) -> bool:
        raise NotImplementedError(self)


class IController(object):
    def register_mediator(self, mediator: IMediator) -> None:
        raise NotImplementedError(self)

    def retrieve_mediator(self, mediator_name: str) -> Union[IMediator, None]:
        raise NotImplementedError(self)

    def remove_mediator(self, mediator_name: str) -> Union[IMediator, None]:
        raise NotImplementedError(self)

    def has_mediator(self, mediator_name: str) -> bool:
        raise NotImplementedError(self)


class IFacade(INotifier):
    def register_proxy(self, proxy: IProxy) -> None:
        raise NotImplementedError(self)

    def remove_proxy(self, proxy_name: str) -> Union[IProxy, None]:
        raise NotImplementedError(self)

    def retrieve_proxy(self, proxy_name: str) -> Union[IProxy, None]:
        raise NotImplementedError(self)

    def has_proxy(self, proxy_name: str) -> bool:
        raise NotImplementedError(self)

    def register_mediator(self, mediator: IMediator) -> None:
        raise NotImplementedError(self)

    def remove_mediator(self, mediator_name: str) -> Union[IMediator, None]:
        raise NotImplementedError(self)

    def retrieve_mediator(self, mediator_name: str) -> Union[IMediator, None]:
        raise NotImplementedError(self)

    def has_mediator(self, mediator_name: str) -> bool:
        raise NotImplementedError(self)

    def register_observer(self, notification_name: str, observer: IObserver) -> None:
        raise NotImplementedError(self)

    def remove_observer(self, notification_name: str, context: object) -> None:
        raise NotImplementedError(self)

    def notify_observer(self, notification: INotification) -> None:
        raise NotImplementedError(self)

    # overwrite
    def send_notification(self, notification_name: str, body: object = None, note_type: str = None) -> None:
        raise NotImplementedError(self)
