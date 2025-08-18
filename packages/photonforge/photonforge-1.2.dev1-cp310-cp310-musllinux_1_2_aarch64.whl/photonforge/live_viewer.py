import logging as _log
import queue as _q
import threading as _t
import time as _time
import typing as _typ
import warnings as _warn

try:
    import flask as _f
    import flask_cors as _fc
    from werkzeug.serving import make_server as _make_server

    _flask_available = True
except ImportError:
    _flask_available = False
    _warn.warn(
        "The 'live_viewer' submodule requires more dependencies than the base photonforge module. "
        "Please install all dependencies by, e.g., 'pip install photonforge[live_viewer]'.",
        stacklevel=2,
    )


class LiveViewer:
    """Live viewer for PhotonForge objects.

    Args:
        port: Port number used by the viewer server.
        start: If ``True``, the viewer server is automatically started.

    Example:
        >>> from photonforge.live_viewer import LiveViewer
        >>> viewer = LiveViewer()

        >>> component = pf.parametric.straight(port_spec="Strip", length=3)
        >>> viewer(component)

        >>> terminal = pf.Terminal("METAL", pf.Circle(2))
        >>> viewer(terminal)
    """

    def __init__(self, port: int = 5001, start: bool = True):
        if not _flask_available:
            return
        self.app = _f.Flask(__name__)
        _fc.CORS(self.app)
        self.port = port
        self.queue = _q.Queue()
        self.current_data = ""
        self.server = None

        log = _log.getLogger("werkzeug")
        log.setLevel(_log.ERROR)

        @self.app.route("/")
        def home():
            return _f.render_template("index.html")

        @self.app.route("/events")
        def events():
            def generate():
                while self.server is not None:
                    try:
                        while not self.queue.empty():
                            self.current_data = self.queue.get_nowait()
                    except _q.Empty:
                        pass
                    if self.current_data:
                        yield f"data: {self.current_data}\n\n"
                    else:
                        yield "data: Waiting for data…\n\n"
                    _time.sleep(0.25)

            return _f.Response(generate(), mimetype="text/event-stream")

        if start:
            self.start()

    def _run_server(self):
        self.server = _make_server("0.0.0.0", self.port, self.app)
        self.server.serve_forever()

    def start(self) -> "LiveViewer":
        """Start the server."""
        if not _flask_available:
            return
        print(f"Starting live viewer at http://localhost:{self.port}")
        # Don't mark this thread as daemon, so it keeps the process alive.
        self.server_thread = _t.Thread(target=self._run_server)
        self.server_thread.daemon = False
        self.server_thread.start()
        return self

    def stop(self):
        """Stop the server."""
        if not _flask_available:
            return
        if self.server is not None:
            self.server.shutdown()
            self.server = None
            print("Server stopped successfully")

    def __call__(self, item: _typ.Any) -> _typ.Any:
        """Display an item with an SVG representation.

        Args:
            item: Item to be displayed.

        Returns:
            'item'.
        """
        if _flask_available and self.server is not None and hasattr(item, "_repr_svg_"):
            self.queue.put(item._repr_svg_())
        return item

    def display(self, item: _typ.Any) -> _typ.Any:
        """Display an item with an SVG representation.

        Args:
            item: Item to be displayed.

        Returns:
            'item'.
        """
        return self(item)

    def _repr_html_(self) -> str:
        """Returns a clickable link for Jupyter."""
        if not _flask_available:
            return "LiveViewer dependencies not installed."
        if self.server is None:
            return "LiveViewer not started."
        return (
            f'Live viewer at <a href="http://localhost:{self.server.port}" target="_blank">'
            f"http://localhost:{self.server.port}</a>"
        )

    def __str__(self) -> str:
        if not _flask_available:
            return "LiveViewer dependencies not installed."
        if self.server is None:
            return "LiveViewer not started."
        return f"Live viewer at http://localhost:{self.server.port}"
