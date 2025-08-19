from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Input, Label, Log, Placeholder, Static, TextArea

from .messages import StdoutMessageFromRepl


class IOArea(Static):
    DEFAULT_CSS = """
    IOArea {
        dock: right;
        width: 20%;
        min-width: 40;
        border-left:tall grey
    }

    Label {
        color: grey;
    }

    #stdin {
        padding: 1 0 0 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="io"):
            yield Label("stdout from remote")
            yield Log()
            # yield Label("stdin to remote", id="stdin")
            # yield Input()

    # StdoutMessageFromRepl
    def on_stdout_message_from_repl(self, message: StdoutMessageFromRepl):
        self.query_one(Log).write(message.text)
