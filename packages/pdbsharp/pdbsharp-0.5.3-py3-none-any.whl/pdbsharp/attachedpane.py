import _colorize
import argparse
import asyncio
import atexit
import importlib
import importlib.metadata
import json

## attach() imports
import os
import pdb
import socket
import stat
import sys
import tempfile
import textwrap
from contextlib import ExitStack, closing
from io import StringIO
from math import remainder
from multiprocessing import Value
from pathlib import Path
from subprocess import PIPE, Popen
from typing import TYPE_CHECKING, Iterable

from textual import log
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, Static, TabbedContent, TabPane
from textual.worker import Worker, get_current_worker

from .debuginputarea import DebugInputArea, DebugInputWidget
from .debugresponsearea import DebugResponseArea
from .IOarea import IOArea
from .messages import (
    MessageFromRepl,
    MessageToRepl,
    PdbMessageType,
    PdbState,
    StdoutMessageFromRepl,
    TabDeleteMessage,
)
from .process_utils import get_process_name
from .wrappedclient import WrappedClient

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class AttachedPane(Container):
    prompt: reactive[str] = reactive("", init=False)

    BINDINGS = [
        Binding("ctrl+d", "detach", "Detach from Process", priority=True),
    ]

    def __init__(
        self,
        *args,
        attach_to: int | None = None,
        capture_io=False,
        commands: Iterable[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.pdbmode = PdbState.Unattached
        self._client: WrappedClient | None = None
        self._server_pid: int | None = None
        self._exitstack = ExitStack()
        self.command_list = list(commands) if commands else []
        self._start_captured_io = capture_io
        self._remote_stdout = tempfile.NamedTemporaryFile("w+", delete_on_close=False)
        self._remote_stdin = tempfile.NamedTemporaryFile("r+", delete_on_close=False)
        self._first_focused = False

        atexit.register(self._exitstack.close)

        def _close_client():
            if self._client and self._client.server_socket:
                return self._client.server_socket.close
            else:
                return lambda *args, **kwargs: 0

        atexit.register(_close_client)

        self._attach_to = attach_to
        self._server_pid = attach_to

        self._pdb_readline_worker: Worker | None = None
        self._stdout_worker: Worker | None = None
        self._quitting = False
        atexit.register(self.quit)

    def compose(self) -> ComposeResult:
        # self.app.sub_title = f"{get_process_name(self._server_pid) if self._server_pid else 'process'} (pid {self._server_pid if self._server_pid else '*unknown*'})"
        with Horizontal():
            with Vertical(id="primary"):
                yield DebugResponseArea()
                yield DebugInputArea().data_bind(AttachedPane.prompt)
                yield IOArea(classes="hidden")

    def on_message_to_repl(self, message: MessageToRepl) -> None:
        if self._client:
            match message.type:
                case PdbMessageType.COMMAND:
                    self._client._send(reply=message.content)
                case PdbMessageType.INT:
                    self._client.send_interrupt()
                case _:
                    raise ValueError(f"Unknown message type {message.type.name}")

    def on_mount(self):
        if self._attach_to:
            self.attach(self._attach_to, capture_io=self._start_captured_io)

    def on_message_from_repl(self, message: MessageFromRepl):
        payload: dict[str, str | list[str]] = json.loads(message.text)
        match payload:
            case {"type": "pdbsharp", "message": str(msg)}:
                self.query_one(DebugResponseArea).write(f"{self.prompt}{msg}")
            case {"type": "info", "message": str(msg)}:
                self.query_one(DebugResponseArea).write(msg)
            case {"type": "error", "message": str(msg)}:
                self.query_one(DebugResponseArea).write("ERROR FROM PDB: " + msg)
            case {"command_list": list(_command_list)}:
                self.command_list = _command_list[:]
            case {"state": str(state), "prompt": str(prompt)}:
                self.prompt = prompt
            case _:
                raise ValueError(
                    f"Could not determine how to handle message from remote pdb: {payload}"
                )

    def attach(self, pid, commands=(), capture_io=False):
        if self.pdbmode in (PdbState.Attached, PdbState.Attaching):
            raise ValueError(f"Already in state {self.pdbmode} and trying to attach()")
        """Attach to a running process with the given PID."""
        """Based on original PdbClient's attach method"""
        self.pdbmode = PdbState.Attaching
        server = self._exitstack.enter_context(
            closing(socket.create_server(("localhost", 0)))
        )

        port = server.getsockname()[1]

        connect_script = self._exitstack.enter_context(
            tempfile.NamedTemporaryFile("w", delete=False)
        )

        use_signal_thread = sys.platform == "win32"
        colorize = _colorize.can_colorize()

        connect_script.write(
            textwrap.dedent(
                f"""
                import pdb, sys
                pdb._connect(
                    host="localhost",
                    port={port},
                    frame=sys._getframe(1),
                    commands={json.dumps("\n".join(commands))},
                    version={pdb._PdbServer.protocol_version()},
                    signal_raising_thread={use_signal_thread!r},
                    colorize={colorize!r},
                )
                """
            )
        )
        connect_script.close()
        orig_mode = os.stat(connect_script.name).st_mode
        os.chmod(connect_script.name, orig_mode | stat.S_IROTH | stat.S_IRGRP)
        try:
            sys.remote_exec(pid, connect_script.name)
        except RuntimeError as err:
            raise err

        # TODO Add a timeout? Or don't bother since the user can ^C?
        client_sock, _ = server.accept()
        self._exitstack.enter_context(closing(client_sock))

        if use_signal_thread:
            interrupt_sock, _ = server.accept()
            self._exitstack.enter_context(closing(interrupt_sock))
            interrupt_sock.setblocking(False)
        else:
            interrupt_sock = None

        # Dropped the call to cmdloop() at the end of this
        self._client = WrappedClient(self, pid, client_sock, interrupt_sock)

        self._server_pid = pid
        self.pdbmode = PdbState.Attached
        if capture_io:
            self.capture_io()
        self._pdb_readline_worker = self.run_worker(self.readline_from_pdb, thread=True)

        self._exitstack.push(self._detach_and_close)

    def _detach_and_close(self, *args):
        if self._client:
            self._client._send(signal="INT")
        self._exitstack.close()

    def detach(self, *args):
        self._detach_and_close()
        self._client = None
        self.pdbmode = PdbState.Unattached
        self.post_message(TabDeleteMessage(self.parent.id))

    async def readline_from_pdb(self, prewait=0.25):
        if self._quitting:
            return

        while not self._client:
            if self._quitting:
                return
            await asyncio.sleep(0.25)

        await asyncio.sleep(prewait)
        log("About to _readline")
        while not get_current_worker().is_cancelled and not self._quitting:
            res = self._client._readline()
            if res:
                self.post_message(MessageFromRepl(res.decode("utf-8")))

    def stdout_reader_factory(self, filepath: str | Path, pause=0.1):
        async def inner():
            """Read input in from a file (_remote_stdout) and send it to the capture output, if any"""
            if self._quitting or not self._client:
                return

            while not get_current_worker().is_cancelled and not self._quitting:
                with open(filepath, "r") as f:
                    data = f.read().lstrip("\x00")
                if data:
                    if not "\n" in data:
                        data = "\n" + data
                    try:
                        self.query_one(IOArea).post_message(StdoutMessageFromRepl(data))
                    except NoMatches:
                        pass
                    else:
                        open(filepath, "w").close()  # clear file
                await asyncio.sleep(pause)

        return inner

    def on_debug_input_widget_capture_message(self, _: DebugInputWidget.CaptureMessage):
        self.capture_io()

    def on_debug_input_widget_uncapture_message(
        self, _: DebugInputWidget.UncaptureMessage
    ):
        self.uncapture_io()

    def capture_io(self):
        if not (self._client and self._server_pid):
            return

        io_capture_script = self._exitstack.enter_context(
            tempfile.NamedTemporaryFile("w", delete=False)
        )

        src = textwrap.dedent(f"""
            import atexit
            from contextlib import ExitStack, closing
            import socket
            import os
            import sys

            class Unbuffered(object):
                def __init__(self, stream):
                    self.stream = stream
                def write(self, data):
                    self.stream.write(data)
                    self.stream.flush()
                def writelines(self, data):
                    self.stream.writelines(data)
                    self.stream.flush()
                def __getattr__(self, attr):
                    return getattr(self.stream, attr)

            os.environ['PYTHONUNBUFFERED'] = '1'

            _pdbsharp_orig_stdout = sys.stdout
            #_pdbsharp_orig_stdin = sys.stdin

            _exitstack = ExitStack()

            def _restore_sys_at_close():
                sys.stdout = _pdbsharp_orig_stdout
                #sys.stdin = _pdbsharp_orig_stdin
                _exitstack.close()

            sys._restore_sys_at_close = _restore_sys_at_close

            atexit.register(_restore_sys_at_close)

            print("Redirecting stdout to {self._remote_stdout.name} for pdb#")

            sys.stdout = _exitstack.enter_context(closing(open("{self._remote_stdout.name}", "w")))
            #sys.stdin = _exitstack.enter_context(closing(open("{self._remote_stdin.name}", "r")))

            sys.stdout = Unbuffered(sys.stdout)
            """)
        io_capture_script.write(src)
        io_capture_script.close()
        orig_mode = os.stat(io_capture_script.name).st_mode
        os.chmod(io_capture_script.name, orig_mode | stat.S_IROTH | stat.S_IRGRP)
        try:
            sys.remote_exec(self._server_pid, io_capture_script.name)
        except RuntimeError as err:
            raise err

        self._exitstack.callback(self.uncapture_io)
        self._stdout_worker = self.run_worker(
            self.stdout_reader_factory(self._remote_stdout.name), thread=True
        )
        try:
            self.query_one(IOArea).remove_class("hidden")
        except NoMatches:
            pass

    def uncapture_io(self):
        # Kill the worker reading std from remote process from tempfile
        if not self._stdout_worker or not self._server_pid:
            return
        if not self._stdout_worker.is_cancelled:
            self._stdout_worker.cancel()

        io_release_script = self._exitstack.enter_context(
            tempfile.NamedTemporaryFile("w", delete=False)
        )
        # Try to call the earlier implemented
        src = textwrap.dedent(
            """
            import sys

            try:
                sys._restore_sys_at_close()
            except AttributeError as err:
                raise err
            """
        )
        io_release_script.write(src)
        io_release_script.close()
        orig_mode = os.stat(io_release_script.name).st_mode
        os.chmod(io_release_script.name, orig_mode | stat.S_IROTH | stat.S_IRGRP)
        try:
            sys.remote_exec(self._server_pid, io_release_script.name)
        except RuntimeError as err:
            raise err
        try:
            self.query_exactly_one(IOArea).add_class("hidden")
        except NoMatches:
            pass

    def action_quit(self):
        self.quit()
        exit()

    def quit(self):
        self._quitting = True
        if self._client:
            self._client._send(signal="INT")
        if self._pdb_readline_worker:
            self._pdb_readline_worker.cancel()
        if self._stdout_worker:
            self._stdout_worker.cancel()

        self.uncapture_io()

    def action_detach(self) -> None:
        self.detach()
