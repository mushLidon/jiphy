from enum import Enum, auto
from functools import partial
from typing import List

from sanic.models.futures import FutureListener


class ListenerEvent(str, Enum):
    def _generate_next_value_(name: str, *args) -> str:  # type: ignore
        return name.lower()

    BEFORE_SERVER_START = auto()
    AFTER_SERVER_START = auto()
    BEFORE_SERVER_STOP = auto()
    AFTER_SERVER_STOP = auto()


class ListenerMixin:
    def __init__(self, *args, **kwargs) -> None:
        self._future_listeners: List[FutureListener] = list()

    def _apply_listener(self, listener: FutureListener):
        raise NotImplementedError  # noqa

    def listener(self, listener_or_event, event_or_none=None, apply=True):
        """Create a listener from a decorated function.

        :param event: Event to listen to.
        """

        def register_listener(listener, event):
            nonlocal apply

            future_listener = FutureListener(listener, event)
            self._future_listeners.append(future_listener)
            if apply:
                self._apply_listener(future_listener)
            return listener

        if callable(listener_or_event):
            return register_listener(listener_or_event, event_or_none)
        else:
            return partial(register_listener, event=listener_or_event)

    def before_server_start(self, listener):
        return self.listener(listener, "before_server_start")

    def after_server_start(self, listener):
        return self.listener(listener, "after_server_start")

    def before_server_stop(self, listener):
        return self.listener(listener, "before_server_stop")

    def after_server_stop(self, listener):
        return self.listener(listener, "after_server_stop")
