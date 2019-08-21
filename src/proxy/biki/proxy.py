from src.pure_framework.patterns.proxy import Proxy, IProxy
from src.pure_framework.patterns.observer import Observer
from src.pure_framework.interfaces import IFacade, INotification
from src.base.events import EvtAppReady


class BikiProxy(Proxy, IProxy):
    NAME = "BikiProxy"

    def __init__(self, facade: IFacade):
        super(BikiProxy, self).__init__(BikiProxy.NAME, facade)

        self._observer = Observer(self.on_notification, self)

    def on_register(self) -> None:
        super(BikiProxy, self).on_register()

        self._facade.register_observer(EvtAppReady, self._observer)

    def on_remove(self) -> None:
        super(BikiProxy, self).on_remove()

        self._facade.remove_observer(EvtAppReady, self)

    def on_notification(self, notification: INotification) -> None:
        name = notification.get_name()
        if name == EvtAppReady:
            print("app ready")
            self.on_appready_event(notification.get_body())

    def on_appready_event(self, body: object) -> None:
        pass

    def get_count(self) -> int:
        return 11
