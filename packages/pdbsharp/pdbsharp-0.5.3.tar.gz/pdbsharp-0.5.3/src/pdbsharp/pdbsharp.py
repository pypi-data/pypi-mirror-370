# Imports are separated into those needed specifically for attach()
# For easier decoupling if that ever can be removed/simplified
import argparse
from contextlib import ExitStack
import importlib
import importlib.metadata
from subprocess import Popen, PIPE
import atexit
import sys

## attach() imports

from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.widgets import Input, TabbedContent, TabPane, Header, Footer, Tabs
from textual.worker import Worker, get_current_worker

from .attachedpane import AttachedPane
from .detachedpane import DetachedPane
from .messages import PdbState, TabFocusMessage, TabDeleteMessage, TabAddMessage
from .debugresponsearea import DebugResponseArea
from .detachedpane import DetachedPane
from .wrappedtabpane import WrappedTabPane


class Pdbsharp(App):
    # MODES = {"detached": DetachedPane, "attached": AttachedPane}
    # DEFAULT_MODE = "detached"

    CSS_PATH = ["styles.tcss", "attachedpane.tcss", "detachedpane.tcss"]

    def __init__(
        self, *args, attach_to=None, capture_io=False, commands=None, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.title = "pdb#"
        self.first_mount = True
        self.starting_args = {
            "attach_to": attach_to,
            "capture_io": capture_io,
            "commands": commands,
        }

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            yield WrappedTabPane("Processes", DetachedPane(), id="processpane")
            # Other panes will be added here
        yield Footer()

    async def on_mount(self):
        if self.first_mount:
            self.first_mount = False
            # self.query_one(DetachedPane).query_one(Input).focus()
            if self.starting_args["attach_to"]:
                self.post_message(
                    TabAddMessage(
                        # await self.attach_in_new_pane(
                        pid=self.starting_args["attach_to"],
                        capture_io=self.starting_args["capture_io"],
                        commands=self.starting_args["commands"],
                    )
                )

    def debug(self, msg: str):
        try:
            self.screen.query_one(DebugResponseArea).write(f"DEBUG: {msg}")
        except NoMatches as err:
            self.notify(msg)

    async def on_tab_add_message(self, msg: TabAddMessage):
        await self.attach_in_new_pane(
            pid=msg.pid, capture_io=msg.capture_io, commands=msg.commands
        )

    async def attach_in_new_pane(self, pid, capture_io=False, commands=None):
        new_pane = WrappedTabPane(
            str(pid),
            AttachedPane(attach_to=pid, capture_io=capture_io, commands=commands),
            id=f"pane_{pid}",
        )
        tc = self.query_one(TabbedContent)
        await tc.add_pane(new_pane)
        self.post_message(TabFocusMessage(tab_id=f"pane_{pid}"))

    def on_tab_focus_message(self, msg: TabFocusMessage):
        tc = self.get_child_by_type(TabbedContent)
        tc.active = msg.tab_id
        if msg.query:
            tc.get_pane(msg.tab_id).query_children(msg.query).focus()

    def on_tab_delete_message(self, msg: TabDeleteMessage):
        tc = self.get_child_by_type(TabbedContent)
        tc.remove_pane(msg.tab_id)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version",
    )
    parser.add_argument(
        "-p",
        "--pid",
        type=int,
        help="The PID of a Python process to connect to",
    )
    parser.add_argument(
        "-m",
        type=str,
        metavar="module",
        dest="module",
    )
    parser.add_argument("-c", "--capture-io", action="store_true", dest="capture_io")

    try:
        idx = sys.argv.index("-m")
    except ValueError:
        args, _ = parser.parse_known_args()
    else:
        # If we're using the -m flag, everything after the module name should be passed to the module being run and not processed as an argument to pdbsharp
        args, _ = parser.parse_known_args(sys.argv[: idx + 2])

    # -c must have -p flag
    if args.capture_io and not args.pid:
        raise AttributeError("--capture-io flag can only be used with --pid")

    return args


def run(args, auto_pilot=None):
    if args.version:
        print(f"pdbsharp {importlib.metadata.version('pdbsharp')}")
        return

    exitstack = ExitStack()
    atexit.register(exitstack.close)
    _process = None

    # Check for flag compatibility
    if args.module and args.pid:
        raise AttributeError("-m and --pid options cannot be used together")
    if args.module:
        file = args.module
        # If we're using the -m flag, everything after the module name should be passed to the module being run
        idx = sys.argv.index("-m")
        module_args = sys.argv[idx + 2 :] if len(sys.argv) >= idx + 2 else []
        _process = Popen(
            [sys.executable, "-m", file] + module_args,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE,
            env={"PYTHONUNBUFFERED": "1"},
        )
        exitstack.callback(lambda *args: _process.terminate)
        args.pid = int(_process.pid)

    app = Pdbsharp(attach_to=args.pid, capture_io=args.capture_io)
    app.run(auto_pilot=auto_pilot)


def main(auto_pilot=None):
    args = parse_args()
    return run(args, auto_pilot)


if __name__ == "__main__":
    main()
