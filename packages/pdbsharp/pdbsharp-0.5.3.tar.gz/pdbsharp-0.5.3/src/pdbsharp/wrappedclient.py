import pdb
import selectors
import typing

from textual.app import App
from textual.message import Message
from textual.worker import get_current_worker


class WrappedClient(pdb._PdbClient):
    def __init__(self, app, *args, **kwargs) -> None:
        self.app: App = app
        super().__init__(*args, **kwargs)
        self.server_socket.setblocking(False)

    def prompt_for_reply(self, prompt):
        pass

    def _readline(self):
        if self.sigint_received:
            # There's a pending unhandled SIGINT. Handle it now.
            self.sigint_received = False
            raise KeyboardInterrupt

        # Wait for either a SIGINT or a line or EOF from the PDB server.
        selector = selectors.DefaultSelector()
        self.server_socket.setblocking(False)
        selector.register(self.server_socket, selectors.EVENT_READ)

        while b"\n" not in self.read_buf and not get_current_worker().is_cancelled:
            for key, _ in selector.select(timeout=0):
                if key.fileobj == self.server_socket:
                    self.server_socket.setblocking(False)
                    try:
                        data = self.server_socket.recv(16 * 1024)
                    except TimeoutError:
                        data = b""
                    else:
                        self.read_buf += data
                        if not data and b"\n" not in self.read_buf:
                            # EOF without a full final line. Drop the partial line.
                            self.read_buf = b""
                            return b""

        ret, sep, self.read_buf = self.read_buf.partition(b"\n")
        return ret + sep
