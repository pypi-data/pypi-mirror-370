from textual import events
from textual.widgets import TabPane


class WrappedTabPane(TabPane):
    def _on_descendant_focus(self, event: events.DescendantFocus):
        event.stop()
        event.prevent_default()
