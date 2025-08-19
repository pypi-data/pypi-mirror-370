from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.layouts import horizontal
from textual.widget import Widget
from textual.widgets import Label, Log, Static

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class DebugResponseArea(Widget):
    def __init__(self, *args, **kwargs) -> None:
        self.app: Pdbsharp
        super().__init__(*args, **kwargs)

    def compose(self):
        self._log = Log(
            #    auto_scroll=True,
        )
        yield self._log

    def write(self, obj):
        self._log.write_line(str(obj))

    def clear(self):
        self._log.clear()
