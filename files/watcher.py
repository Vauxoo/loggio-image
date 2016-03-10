
import logging
from os import path, environ
import socket
import sys
import time
from pygtail import Pygtail
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


_logger = logging.getLogger('watcher')
_logger.setLevel(logging.DEBUG)


class LogEventHandler(FileSystemEventHandler):
    """ In case of any change this class is used to stream the changes to the logio server,
        as the script and the server will be in the same container by default is streamed to
        localhost.

        Creates a stream per file and a node with the proper env var
    """

    def __init__(self):
        super(LogEventHandler, self).__init__()
        self._socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(("localhost", 28777))
        self._node = environ.get("NODE", "runbot").strip()
        self._register_node()

    def _register_node(self):
        message = "+node|{node}\r\n".format(node=self._node)
        self._socket.sendall(message)

    def _unregister_node(self):
        message = "-node|{node}\r\n".format(node=self._node)
        self._socket.sendall(message)

    def on_modified(self, event):
        _logger.debug("File change detected: %s", event.src_path)
        sys.stdout.write("Changed: %s"%event.src_path)
        if not event.src_path.endswith('.offset') and path.isfile(event.src_path):
            file_name = path.basename(event.src_path)
            offset_file = '{name}.offset'.format(name=file_name)
            for line in Pygtail(event.src_path, offset_file=path.join('/tmp', offset_file)):
                self.stream_line(file_name, 'info', line)

    def stop(self):
        self._unregister_node()
        self._socket.close()

    def stream_line(self, stream, level, line):
        message = "+log|{stream}|{node}|{level}|{text}\r\n".format(
            stream=stream, node=self._node, text=line.strip(), level=level
        )
        _logger.debug("Sending message: %s", message)
        self._socket.sendall(message)


class MasterMonitor(Observer):
    """ Monitor a folder waiting for changes in any file (not recursive)
    """
    _path = '/logs'

    def __init__(self, path_to_logs=None):
        if path_to_logs is not None:
            self._path = path_to_logs
        super(MasterMonitor, self).__init__()
        self._event_handler = LogEventHandler()

    def start_monitor(self):
        _logger.debug("Watching: %s", self._path)
        self.schedule(self._event_handler, self._path,  recursive=False)
        self.start()

    def stop_monitor(self):
        self.stop()
        self._event_handler.stop()


def main():
    _logger.info("Starting monitor")
    mmonitor = MasterMonitor()
    mmonitor.start_monitor()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        _logger.info("Keyboard interrupt, shutting down")
        mmonitor.stop_monitor()
    mmonitor.join()


if __name__ == '__main__':
    main()
