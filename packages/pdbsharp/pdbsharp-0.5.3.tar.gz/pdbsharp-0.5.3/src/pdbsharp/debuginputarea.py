import json
from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Label

from .messages import MessageFromRepl, MessageToRepl, PdbMessageType

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class DebugInputWidget(Input):
    class CaptureMessage(Message):
        def __init__(self):
            super().__init__()

    class UncaptureMessage(Message):
        def __init__(self):
            super().__init__()

    BINDINGS = [
        ("ctrl+c", "interrupt", "Send Ctrl+C"),
    ]

    def action_interrupt(self):
        self.post_message(MessageToRepl(type=PdbMessageType.INT))
        self.value = ""

    def action_submit(self):
        if not self.handle_custom_command(self.value):
            self.post_message(
                MessageToRepl(type=PdbMessageType.COMMAND, content=self.value)
            )
            self.post_message(
                MessageFromRepl(json.dumps({"type": "pdbsharp", "message": self.value}))
            )
        self.value = ""

    def handle_custom_command(self, value) -> bool:
        """Handle all internal Pdb# special commands

        Returns:
            bool: True if a custom command was handled; false if not
        """
        if value == "capture":
            self.post_message(self.CaptureMessage())
            self.app.debug("Attempting to start IO capture")
            return True
        elif value == "uncapture":
            self.post_message(self.UncaptureMessage())
            self.app.debug("Attempting to uncapture IO")
            return True
        return False


class DebugInputArea(Widget):
    app: Pdbsharp
    prompt: reactive[str] = reactive("", init=False)

    def watch_prompt(self, old: str, new: str) -> None:
        if "Pdb" in new:
            new = new.replace("Pdb", "Pdb#")
        self.query_one(Label).update(new)

    def compose(self):
        with Horizontal():
            yield Label(self.prompt if self.prompt else "(-)")
            yield DebugInputWidget()
