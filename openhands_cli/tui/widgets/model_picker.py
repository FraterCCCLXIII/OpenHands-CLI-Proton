"""Model and Cloud picker Select widgets with compact styling."""

from __future__ import annotations

from textual import events
from textual.app import ComposeResult
from textual.widgets import Select
from textual.widgets._select import SelectCurrent

from openhands_cli.tui.widgets.checkmark_select import (
    CloudPickerOverlay,
    ModelPickerOverlay,
)


class ModelPickerSelect(Select[str]):
    """Select widget that uses ModelPickerOverlay."""

    def compose(self) -> ComposeResult:
        yield SelectCurrent(self.prompt)
        yield ModelPickerOverlay(type_to_search=self._type_to_search).data_bind(
            compact=Select.compact
        )

    def _on_mouse_down(self, event: events.MouseDown) -> None:
        if not self.expanded:

            def _open_if_still_closed() -> None:
                if not self.expanded:
                    self.focus()
                    self.action_show_overlay()

            self.call_after_refresh(_open_if_still_closed)


class CloudPickerSelect(Select[str]):
    """Select widget whose overlay renders separators as proper border T-junctions."""

    def compose(self) -> ComposeResult:
        yield SelectCurrent(self.prompt)
        yield CloudPickerOverlay(type_to_search=self._type_to_search).data_bind(
            compact=Select.compact
        )

    def _on_mouse_down(self, event: events.MouseDown) -> None:
        if not self.expanded:

            def _open_if_still_closed() -> None:
                if not self.expanded:
                    self.focus()
                    self.action_show_overlay()

            self.call_after_refresh(_open_if_still_closed)
