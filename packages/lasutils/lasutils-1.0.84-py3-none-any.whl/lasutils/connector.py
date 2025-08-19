import logging
import os
import signal
from abc import ABC, abstractmethod
from importlib import import_module
import time
from lasutils import exceptions
from lasutils.settings import ConnectorSettings
from lasutils.helpers import sleep_ticker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Connector(ABC):
    def __init__(self, settings: ConnectorSettings):
        self.shutdown = False
        signal.signal(signal.SIGINT, self._exit_gracefully)
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.config = settings.config
        self.secrets = settings.secrets

    def _exit_gracefully(self, signum, frame):
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        logger.info(f"Received {signal_name}, waiting for running tasks to finish...")
        self.shutdown = True

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def run(self, round: int) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


def run_connector(settings: ConnectorSettings):
    """Runs connector class specified as dotted list"""
    if not settings.connector_class:
        raise exceptions.MissingEnvironmentVariable("CLASS")
    mod_name, cls_name = settings.connector_class.rsplit(".", 1)
    cls = getattr(import_module(mod_name), cls_name)
    assert issubclass(cls, Connector)

    app = cls(settings)
    app.start()
    ticker = sleep_ticker(wakeup_interval=settings.config["pollInterval"])
    while not app.shutdown:
        try:
            count = next(ticker)
            app.run(count)
        except KeyboardInterrupt:
            logging.info(f"Time loop interrupted.")
            break
    app.stop()


# def run_connector():
#     """Runs connector class specified as dotted list"""
#     if not settings.POLLER_CLASS:
#         raise exceptions.MissingEnvironmentVariable("CLASS")

#     mod_name, cls_name = settings.POLLER_CLASS.rsplit(".", 1)
#     cls = getattr(import_module(mod_name), cls_name)
#     assert issubclass(cls, Connector)

#     app = cls()
#     app.start()
#     while not app.shutdown:
#         app.run()
#     app.stop()
