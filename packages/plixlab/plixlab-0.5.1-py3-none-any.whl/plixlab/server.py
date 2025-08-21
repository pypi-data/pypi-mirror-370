"""
PlixLab Server Module

This module provides a Tornado-based web server for serving PlixLab presentations.
It includes WebSocket support for real-time data updates and server-sent events
for live reloading during development.
"""
"""
PlixLab Server Module

This module provides a Tornado-based web server for serving PlixLab presentations.
It includes WebSocket support for real-time data updates and server-sent events
for live reloading during development.
"""

import os
import socket
import webbrowser
import msgpack
import threading
from typing import Any, List

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import autoreload, gen
from tornado.iostream import StreamClosedError

# List of active SSE connections
active_sse_connections: List[Any] = []


def get_free_port() -> int:
    """Find an available port assigned by the OS."""
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def make_app(data_provider: Any, hot_reload: bool) -> tornado.web.Application:
    """Construct the Tornado app with all necessary routes."""
    base_dir = os.path.dirname(__file__)
    public_dir = os.path.join(base_dir, "web")

    return tornado.web.Application([
        (r"/", NoCacheHandler, {
            "path": os.path.join(public_dir, "index.html"),
            "port": PLIXLAB_PORT,
            "hot_reload": hot_reload,
        }),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(public_dir, "static")}),
        (r"/assets/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(public_dir, "assets")}),
        (r"/data", ReloadWebSocketHandler, {"data_provider": data_provider}),
        (r"/events", ReadySSEHandler),
        (r"/shutdown", ShutdownHandler),
        (r"/static_data", StaticDataHandler, {"data_provider": data_provider}),
    ])

class ShutdownHandler(tornado.web.RequestHandler):
    def post(self):
        print("Shutdown requested by client")
        self.write("Shutting down...")
        tornado.ioloop.IOLoop.current().add_callback(tornado.ioloop.IOLoop.current().stop)

class NoCacheHandler(tornado.web.RequestHandler):
    """Serves index.html with JS vars injected and no caching."""

    def initialize(self, path: str, port: int, hot_reload: bool) -> None:
        self.file_path = path
        self.port = port
        self.hot_reload = hot_reload

    def set_default_headers(self) -> None:
        self.set_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.set_header("Pragma", "no-cache")
        self.set_header("Expires", "0")

    def get(self) -> None:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                html = f.read()

            injected = f"""
            <script>
                window.PLIXLAB_PORT = {self.port};
                window.PLIXLAB_HOT_RELOAD = {str(self.hot_reload).lower()};
            </script>"""
            html = html.replace("</head>", f"{injected}\n</head>")
            self.write(html)
        else:
            self.set_status(404)
            self.write("404: index.html not found")


class ReloadWebSocketHandler(tornado.websocket.WebSocketHandler):
    """Sends msgpack-encoded presentation data to connected WebSocket clients."""

    def initialize(self, data_provider: Any) -> None:
        self.data_provider = data_provider

    def open(self):
        print("WebSocket connection opened")
        self.write_message(msgpack.packb(self.data_provider), binary=True)

    def on_close(self):
        print("WebSocket connection closed")


class ReadySSEHandler(tornado.web.RequestHandler):
    """SSE handler to notify the frontend that the server is ready."""

    def set_default_headers(self) -> None:
        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")

    async def get(self) -> None:
        global active_sse_connections
        active_sse_connections.append(self)

        try:
            print("SSE client connected")
            self.write("retry: 3000\n")
            self.write("data: ready\n\n")
            await self.flush()

            while True:
                await gen.sleep(10)
                self.write("data: keep-alive\n\n")
                await self.flush()
        except StreamClosedError:
            print("SSE client disconnected")
        finally:
            if self in active_sse_connections:
                active_sse_connections.remove(self)
                print("SSE connection closed")


class StaticDataHandler(tornado.web.RequestHandler):
    """Serves presentation data as a binary blob for static (non-hot-reload) mode."""

    def initialize(self, data_provider: Any):
        self.data_provider = data_provider

    def get(self):
        self.set_header("Content-Type", "application/octet-stream")
        self.write(msgpack.packb(self.data_provider))


def cleanup_connections():
    """Closes all active SSE connections."""
    print("Cleaning up SSE connections...")
    for conn in active_sse_connections:
        try:
            conn.finish()
        except Exception as e:
            print(f"Error closing SSE connection: {e}")
    active_sse_connections.clear()

def run(data_provider: Any, hot_reload: bool = False, carousel: bool = False):
    """
    Launch the Tornado server to serve PlixLab presentations.

    Args:
        data_provider: Serializable content
        hot_reload (bool): Enable autoreload for development (default False)
        carousel (bool): Enable carousel mode for slides (default False)
    """

    global PLIXLAB_PORT
    PLIXLAB_PORT = 8889 if hot_reload else get_free_port()

    print(f"Starting PlixLab server on port {PLIXLAB_PORT} (hot_reload={hot_reload})")
    app = make_app(data_provider, hot_reload)
    app.listen(PLIXLAB_PORT)

    url = f"http://localhost:{PLIXLAB_PORT}"
    if carousel:
        url += "?carousel=True"

    if os.environ.get("PLIXLAB_BROWSER_OPENED") != "1":
     webbrowser.open(url)
     os.environ["PLIXLAB_BROWSER_OPENED"] = "1"    

    if hot_reload:
        autoreload.add_reload_hook(cleanup_connections)
        autoreload.add_reload_hook(lambda: tornado.ioloop.IOLoop.current().stop())
        autoreload.start()
        print("Hot reload enabled on port 8889")
    else:
        print("Hot reload disabled. Using random port.")

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Shutting down...")
    finally:
        cleanup_connections()

