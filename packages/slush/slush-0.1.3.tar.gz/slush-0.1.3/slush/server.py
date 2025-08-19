# slush/server.py
import os
import sys
from wsgiref.simple_server import make_server
from threading import Thread

def run(app, host="127.0.0.1", port=8000, reload=True):
    """
    Run a WSGI application with optional auto-reloading using Watchdog.
    :param app: WSGI application instance
    :param host: Hostname to bind to
    :param port: Port number to bind to
    :param reload: Enable auto-reloading of the server
    """
    if reload:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            raise ImportError("⚠️ Auto-reload requires 'watchdog'. Install it using 'pip install watchdog'.")

        class ReloadHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path.endswith(".py"):
                    print(f"🔄 Detected change in {event.src_path}. Restarting...")
                    observer.stop()
                    os.execv(sys.executable, [sys.executable] + sys.argv)

        observer = Observer()
        observer.schedule(ReloadHandler(), path='.', recursive=True)
        observer.start()

        print(f"🚀 Slush server started with auto-reload: http://{host}:{port}")
        try:
            _start_server(app, host, port)
        finally:
            observer.stop()
            observer.join()
    else:
        print(f"🚀 Slush server running on http://{host}:{port}")
        _start_server(app, host, port)


def _start_server(app, host, port):
    with make_server(host, port, app) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n❌ Server stopped manually.")
