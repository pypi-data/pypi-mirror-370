import datetime

from mosamatic.singleton import singleton


@singleton
class LogManager:
    def __init__(self):
        self._name = 'mosamatic-cli'
        self._listeners = []

    def _log(self, level, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f'[{timestamp}] {level} {self._name}: {message}'
        print(message)
        self.notify_listeners(message)

    def info(self, message):
        self._log('INFO', message)

    def warning(self, message):
        self._log('WARNING', message)

    def error(self, message):
        self._log('ERROR', message)

    def add_listener(self, listener):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def notify_listeners(self, message):
        for listener in self._listeners:
            listener.new_message(message)