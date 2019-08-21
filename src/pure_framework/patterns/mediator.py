from src.pure_framework.interfaces import IMediator, INotifier, IFacade
from src.pure_framework.patterns.observer import Notifier


class Mediator(Notifier, IMediator, INotifier):
    NAME = "Mediator"

    def __init__(self, name: str, facade: IFacade):
        self._facade = facade

        mediator_name = name or self.NAME
        if mediator_name is None:
            raise ValueError("Mediator name cannot be None")

        self._mediator_name = mediator_name

    def get_mediator_name(self) -> str:
        return self._mediator_name

    def on_register(self) -> None:
        pass

    def on_remove(self) -> None:
        pass
