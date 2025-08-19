from logging import Logger
import signal


class SignalHandler:
    def __init__(self, logger: Logger):
        self.received_signal = False
        self.logger = logger
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        self.logger.info(f"Received signal {signal}")
        self.received_signal = True
