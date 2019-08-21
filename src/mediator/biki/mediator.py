from typing import Union
import time
from flask import Flask, request, jsonify
from src.pure_framework.patterns.mediator import Mediator, IMediator
from src.pure_framework.patterns.observer import Observer
from src.pure_framework.interfaces import IFacade, INotification

from src.proxy.biki.proxy import BikiProxy
from src.base.events import EvtInitServer


class BikiMediator(Mediator, IMediator):
    NAME = 'BikiMediator'

    def __init__(self, facade: IFacade):
        super(BikiMediator, self).__init__(BikiMediator.NAME, facade)

        self._observer = Observer(self._on_notification, self)

    def on_register(self) -> None:
        super(BikiMediator, self).on_register()

        self._facade.register_observer(EvtInitServer, self._observer)

    def on_remove(self) -> None:
        super(BikiMediator, self).on_remove()

        self._facade.remove_observer(EvtInitServer, self)

    def _on_notification(self, notification: INotification) -> None:
        name = notification.get_name()
        body = notification.get_body()
        if name == EvtInitServer:
            self._init_server(body['flask_app'])

    def _init_server(self, flask_app: Flask) -> None:
        print("BikiMediator._init_server")
        @flask_app.route('/hello', methods=["GET"])
        def hello():
            try:
                self._on_hello_route().send(None)
            except StopIteration as e:
                print(e.value)
                return e.value

    async def _on_hello_route(self):
        time.sleep(10)
        if not request.args or 'id' not in request.args:
            return jsonify({'success': False, 'error': 'invalid arguments'})

        count = self.biki_proxy().get_count()
        return jsonify({'success': True, 'data': {'count': count, 'id': request.args['id']}})

    def biki_proxy(self) -> Union[BikiProxy, None]:
        proxy = self._facade.retrieve_proxy(BikiProxy.NAME)
        if isinstance(proxy, BikiProxy):
            return proxy

        return None
