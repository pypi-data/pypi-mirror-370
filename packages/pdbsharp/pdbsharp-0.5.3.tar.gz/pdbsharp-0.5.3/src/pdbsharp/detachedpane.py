import asyncio
from textwrap import shorten
from tkinter import Widget
from typing import TYPE_CHECKING, Callable, TypedDict, cast

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    OptionList,
    Static,
    TabbedContent,
    TextArea,
)
from textual.widgets.option_list import Option
from textual.worker import Worker, get_current_worker

from .messages import PdbState, TabAddMessage
from .process_utils import get_python_processes

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class DetachedPane(Static):
    CSS_PATH = "detachedscreen.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_rendered_pids: list[int] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="content"):
            yield Label(
                "Enter the PID of a running Python process to debug:",
                id="intro",
            )
            yield Input(
                "", placeholder="Remote Process PID", type="integer", id="remote-pid"
            )
            yield Label(
                "Or select an existing process:\n[grey][showing processes matching 'python3'][/grey]"
            )
            yield ProcessOptionList(id="processlist")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.value:
            pid = event.input.value
            event.input.value = ""
            self._add_tab_if_not_duplicate(pid)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        prompt = cast(str, event.option.prompt)
        pid, _, _ = prompt.partition(" ")
        self._add_tab_if_not_duplicate(pid)

    def _add_tab_if_not_duplicate(self, pid: str):
        # If tab already exists, jump to it
        try:
            tabbed_content = self.app.query_one(TabbedContent)
            # Raise error if pane doesn't exist
            _ = tabbed_content.get_pane(f"pane_{pid}")
            tabbed_content.active = f"pane_{pid}"
        except NoMatches:  # No matching tab, need to create one
            self.app.post_message(
                TabAddMessage(pid=int(pid), capture_io=False, commands=None)
            )

    async def list_refresher(self):
        while not get_current_worker().is_cancelled:
            await asyncio.sleep(0.5)
            await self.query_one(ProcessOptionList).refresh_options()

    def on_mount(self):
        self._refresh_worker = self.run_worker(
            self.list_refresher, "Options List Refresher"
        )


class ProcessOptionList(OptionList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.highlighted = None
        self.last_pids: list[int] = []

    async def refresh_options(self):
        info = get_python_processes()
        self.show_pids = sorted(int(p["pid"]) for p in info)
        new_pids = sorted(int(p["pid"]) for p in info)
        if new_pids == self.last_pids:
            return
        self.clear_options()
        self.last_pids = new_pids
        self.clear_options()
        # Sort by descending PID order, so that the newest processes are at the top of the list
        key: Callable[[Option], int] = lambda opt: int(opt.prompt.partition(" ")[0])
        self.add_options(
            sorted(
                [
                    Option(
                        f"{p['pid']: <10}{shorten(p['name'], 10): <11}{shorten(p['cmdline'][-1] if p['cmdline'] else '', self.app.size.width - 30)}",
                        id=f"option_{p['pid']}",
                    )
                    for p in info
                ],
                key=key,
                reverse=True,
            )
        )
        await self.recompose()

    def on_focus(self, event):
        self.highlighted = 0

    async def on_mount(self):
        await self.refresh_options()
