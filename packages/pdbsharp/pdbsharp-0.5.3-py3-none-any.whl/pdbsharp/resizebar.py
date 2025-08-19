# MIT License

# Copyright (c) 2025 Textual Tool Yard

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from textual.geometry import clamp
from textual.widget import Widget
from textual.widgets import Static
from typing import Any
from textual.events import MouseMove, MouseDown

class ResizeBar(Static):

    DEFAULT_CSS = """
    ResizeBar {
        width: 1;
        height: 1fr;
        border-left: outer $panel;
        &:hover { border-left: outer $primary-darken-2; }
        &.pressed {   border-left: outer $primary-lighten-1; }
    }
    """

    def __init__(self, parent: Widget, *, min_width=25, max_width=80, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.connected_container = parent
        self.min_width = min_width    # adjust as needed
        self.max_width = max_width
        self.tooltip = "<-- Drag to resize -->"

    def on_mouse_move(self, event: MouseMove) -> None:

        # App.mouse_captured refers to the widget that is currently capturing mouse events.
        if self.app.mouse_captured == self:

            total_delta = event.screen_offset - self.position_on_down
            new_size = self.size_on_down - total_delta
        
            self.connected_container.styles.width = clamp(new_size.width, self.min_width, self.max_width)

    def on_mouse_down(self, event: MouseDown) -> None:

        self.max_width = self.app.screen.size.width - 10
        self.position_on_down = event.screen_offset
        self.size_on_down = self.connected_container.size

        self.add_class("pressed")    # this requires a "pressed" class to exist
        self.capture_mouse()

    def on_mouse_up(self) -> None:

        self.remove_class("pressed")
        self.release_mouse()