from flask import Flask
from src.pure_framework.patterns.facade import Facade
from src.pure_framework.interfaces import IFacade
from src.base.events import EvtAppReady, EvtInitServer

from src.proxy.biki.proxy import BikiProxy

from src.mediator.biki.mediator import BikiMediator


class AppFacade(Facade, IFacade):
    _instance = None

    @staticmethod
    def get_instance():
        if AppFacade._instance is None:
            AppFacade._instance = AppFacade()
            AppFacade._instance._init_proxy()
            AppFacade._instance._init_mediator()

        return AppFacade._instance

    def __init__(self):
        super(AppFacade, self).__init__()

        self._flask_instance = None

    def _init_proxy(self) -> None:
        self.register_proxy(BikiProxy(self))

    def _init_mediator(self) -> None:
        self.register_mediator(BikiMediator(self))

    def init_server(self, flask_app: Flask):
        self.send_notification(EvtInitServer, {'flask_app': flask_app})

    def app_ready(self):
        self.send_notification(EvtAppReady)
