"""Checkmark Select overlay and variants for model/cloud pickers.

Port from prototype - renders a right-aligned ✓ on the active option row
and supports separator rows with T-junction borders.
"""

from __future__ import annotations

from rich.segment import Segment
from rich.style import Style as RichStyle
from textual.geometry import Region
from textual.strip import Strip
from textual.widgets import Select
from textual.widgets._select import SelectOverlay


class CheckmarkSelectOverlay(SelectOverlay):
    """SelectOverlay base that renders a right-aligned ✓ on the active option row."""

    _CHECK_CHAR = "✓"
    _CHECK_COLOR = "#5faf5f"

    def _selected_option_index(self) -> int | None:
        """Return the OptionList index matching the parent Select's current value."""
        parent = self.parent
        if parent is None or not hasattr(parent, "_options") or not hasattr(parent, "value"):
            return None
        value = parent.value
        if value is Select.BLANK:
            return None
        for idx, (_, opt_value) in enumerate(parent._options):
            if opt_value == value:
                return idx
        return None

    def _inject_check(self, strip: Strip) -> Strip:
        """Replace the last content cell of *strip* with the checkmark character."""
        width = strip.cell_length
        if width < 3:
            return strip
        left_part = list(strip.crop(0, width - 2))
        right_border = list(strip)[-1]
        base_style = left_part[-1].style if left_part else RichStyle.null()
        check_seg = Segment(
            self._CHECK_CHAR,
            (base_style or RichStyle.null()) + RichStyle(color=self._CHECK_COLOR),
        )
        return Strip(left_part + [check_seg, right_border], width)

    def _option_widget_y(self, option_index: int, crop: Region) -> int | None:
        """Convert an option index to a crop-relative y coordinate, or None."""
        try:
            content_y = self._index_to_line[option_index] - self.scroll_offset.y
        except KeyError:
            return None
        local_y = content_y + self.styles.gutter.top - crop.y
        return local_y if 0 <= local_y < crop.height else None

    def render_lines(self, crop: Region) -> list[Strip]:
        self._update_lines()
        strips = super().render_lines(crop)
        sel_idx = self._selected_option_index()
        if sel_idx is not None:
            local_y = self._option_widget_y(sel_idx, crop)
            if local_y is not None:
                strips[local_y] = self._inject_check(strips[local_y])
        return strips


class _SeparatorCheckmarkOverlay(CheckmarkSelectOverlay):
    """CheckmarkSelectOverlay that also renders the separator row as border T-junctions."""

    def _sep_index(self) -> int | None:
        """Return the index of the separator option, or None if absent."""
        for i, option in enumerate(self.options):
            prompt = option.prompt
            if isinstance(prompt, str) and prompt.startswith("─"):
                return i
        return None

    def action_cursor_down(self) -> None:
        super().action_cursor_down()
        if self.highlighted == self._sep_index():
            super().action_cursor_down()

    def action_cursor_up(self) -> None:
        super().action_cursor_up()
        if self.highlighted == self._sep_index():
            super().action_cursor_up()

    def render_lines(self, crop: Region) -> list[Strip]:
        strips = super().render_lines(crop)
        sep_index = self._sep_index()
        if sep_index is None:
            return strips
        local_y = self._option_widget_y(sep_index, crop)
        if local_y is None:
            return strips
        segments = list(strips[local_y])
        if len(segments) >= 2:
            border_style = segments[0].style
            new_segments: list[Segment] = []
            for idx, seg in enumerate(segments):
                if idx == 0:
                    new_segments.append(
                        Segment("├" if seg.text == "│" else seg.text, border_style)
                    )
                elif idx == len(segments) - 1:
                    new_segments.append(
                        Segment("┤" if seg.text == "│" else seg.text, border_style)
                    )
                else:
                    new_segments.append(Segment(seg.text, border_style))
            strips[local_y] = Strip(new_segments, strips[local_y].cell_length)
        return strips


class ModelPickerOverlay(_SeparatorCheckmarkOverlay):
    """Overlay for the model picker."""


class CloudPickerOverlay(_SeparatorCheckmarkOverlay):
    """Overlay for the cloud picker."""
