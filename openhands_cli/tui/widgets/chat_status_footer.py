"""Chat status footer showing repo, branch, model, and location.

Port from prototype - displays context info below the chat input.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import var
from textual.widgets import Static

from openhands_cli.cloud.conversation import extract_repository_from_dir
from openhands_cli.locations import get_work_dir
from openhands_cli.tui.modals.settings.choices import get_all_model_options
from openhands_cli.tui.widgets.model_picker import CloudPickerSelect, ModelPickerSelect
from openhands_cli.utils import abbreviate_number, format_cost


if TYPE_CHECKING:
    from openhands.sdk.llm.utils.metrics import Metrics
    from openhands_cli.tui.textual_app import OpenHandsApp


class ChatStatusFooter(Horizontal):
    """Status row below chat input: repo, branch, model picker, location."""

    DEFAULT_CSS = """
    #chat_status_footer {
        height: 1;
        width: 1fr;
        background: transparent;
        color: #f2f2f2;
        padding: 0 1;
        margin: 0;
        align: left middle;
    }

    #status-left {
        width: auto;
        color: #f2f2f2;
    }

    #model-icon {
        width: auto;
        color: #8a8a8a;
        margin-right: 1;
    }

    #model-icon:hover {
        color: #c0c0c0;
    }

    #model-label {
        width: auto;
        color: #f2f2f2;
        margin-right: 0;
    }

    #model-label:hover {
        color: #ffffff;
    }

    #model-picker {
        width: auto;
        min-width: 9;
        border: none;
        background: transparent;
        color: #f2f2f2;
        margin: 0;
        height: 1;
    }

    #model-picker > SelectCurrent {
        width: auto;
        min-width: 9;
        height: 1;
        border: none !important;
        background: transparent;
        background-tint: 0%;
        padding: 0;
    }

    #model-picker > SelectCurrent Static#label {
        width: auto;
    }

    #model-picker > SelectCurrent .arrow {
        width: auto;
        padding: 0 0 0 1;
        color: #8a8a8a;
    }

    #model-shortcut {
        width: auto;
        color: #8a8a8a;
        margin-left: 1;
        margin-right: 0;
    }

    #model-shortcut:hover {
        color: #c0c0c0;
    }

    #model-picker > SelectOverlay {
        width: auto;
        min-width: 24;
        constrain: none inflect;
    }

    #model-picker:hover {
        background: #1e1e1e;
        color: #ffffff;
    }

    #model-picker:hover > SelectCurrent {
        background: #1e1e1e;
        background-tint: 0%;
    }

    #model-picker:focus {
        border: none;
        background: transparent;
        color: #f2f2f2;
    }

    #model-picker:focus > SelectCurrent,
    #model-picker.-expanded > SelectCurrent {
        border: none !important;
        background: transparent;
        background-tint: 0%;
    }

    #cloud-icon {
        width: auto;
        color: #8a8a8a;
        margin-left: 1;
        margin-right: 0;
    }

    #cloud-icon:hover {
        color: #c0c0c0;
    }

    #cloud-label {
        width: auto;
        color: #f2f2f2;
        margin-right: 0;
    }

    #cloud-label:hover {
        color: #ffffff;
    }

    #cloud-picker {
        width: auto;
        min-width: 8;
        border: none;
        background: transparent;
        color: #f2f2f2;
        margin-left: 0;
        height: 1;
    }

    #cloud-picker > SelectCurrent {
        width: auto;
        min-width: 8;
        height: 1;
        border: none !important;
        background: transparent;
        background-tint: 0%;
        padding: 0;
    }

    #cloud-picker > SelectCurrent Static#label {
        width: auto;
    }

    #cloud-picker > SelectCurrent .arrow {
        width: auto;
        padding: 0 0 0 1;
        color: #8a8a8a;
    }

    #cloud-picker > SelectOverlay {
        width: auto;
        min-width: 22;
        padding: 0;
        constrain: none inflect;
    }

    #cloud-picker:hover {
        background: #1e1e1e;
        color: #ffffff;
    }

    #cloud-picker:hover > SelectCurrent {
        background: #1e1e1e;
        background-tint: 0%;
    }

    #cloud-picker:focus {
        border: none;
        background: transparent;
        color: #f2f2f2;
    }

    #cloud-picker:focus > SelectCurrent,
    #cloud-picker.-expanded > SelectCurrent {
        border: none !important;
        background: transparent;
        background-tint: 0%;
    }

    #cloud-shortcut {
        width: auto;
        color: #8a8a8a;
        margin-left: 1;
    }

    #cloud-shortcut:hover {
        color: #c0c0c0;
    }

    #status-right-spacer {
        width: 1fr;
    }

    #chat-meta-stats {
        color: #606060;
        width: auto;
    }
    """

    metrics: var[Metrics | None] = var(None)

    def __init__(self, **kwargs) -> None:
        super().__init__(id="chat_status_footer", **kwargs)

    def watch_metrics(self, _value: Metrics | None) -> None:
        self._update_metrics_display()
        self._refresh_status()  # Also refresh model when metrics update (conversation active)

    def _format_metrics_display(self) -> str:
        if self.metrics is None:
            return "ctx N/A  •  $ 0.00  (↑ 0  ↓ 0  cache N/A)"
        usage = self.metrics.accumulated_token_usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        context_window = usage.context_window if usage else 0
        cache_read_tokens = usage.cache_read_tokens if usage else 0
        accumulated_cost = self.metrics.accumulated_cost or 0.0
        last_request_input_tokens = 0
        if self.metrics.token_usages:
            last_usage = self.metrics.token_usages[-1]
            last_request_input_tokens = last_usage.prompt_tokens or 0
        cache_hit_rate = (
            f"{(cache_read_tokens / input_tokens * 100):.0f}%"
            if input_tokens > 0
            else "N/A"
        )
        if last_request_input_tokens > 0:
            ctx_current = abbreviate_number(last_request_input_tokens)
            ctx_display = (
                f"ctx {ctx_current} / {abbreviate_number(context_window)}"
                if context_window > 0
                else f"ctx {ctx_current}"
            )
        else:
            ctx_display = "ctx N/A"
        return (
            f"{ctx_display}  •  $ {format_cost(accumulated_cost)}  "
            f"(↑ {abbreviate_number(input_tokens)}  "
            f"↓ {abbreviate_number(output_tokens)}  cache {cache_hit_rate})"
        )

    def _update_metrics_display(self) -> None:
        stats = self.query_one("#chat-meta-stats", Static)
        stats.update(self._format_metrics_display())

    def compose(self) -> ComposeResult:
        yield Static("", id="status-left")
        yield Static("✦", id="model-icon")
        yield Static("Model:", id="model-label")
        model_options = get_all_model_options()
        default_model = model_options[0][1] if model_options else "anthropic/claude-sonnet-4-5-20250929"
        yield ModelPickerSelect(
            model_options,
            value=default_model,
            allow_blank=False,
            compact=True,
            id="model-picker",
        )
        yield Static("Ctrl+m", id="model-shortcut")
        yield Static("⛁", id="cloud-icon")
        yield CloudPickerSelect(
            ((" Local", "local"), (" Connect to Cloud", "connect_cloud")),
            value="local",
            allow_blank=False,
            compact=True,
            id="cloud-picker",
        )
        yield Static("Ctrl+c", id="cloud-shortcut")
        yield Static(id="status-right-spacer")
        yield Static("ctx N/A  •  $ 0.00  (↑ 0  ↓ 0  cache N/A)", id="chat-meta-stats")

    def on_mount(self) -> None:
        self._refresh_status()
        self._update_metrics_display()

    def on_resize(self) -> None:
        self._refresh_status()

    def _refresh_status(self) -> None:
        """Update repo/branch and model from app state."""
        work_dir = get_work_dir()
        repo, branch = extract_repository_from_dir(work_dir)
        if repo:
            repo_name = repo.rstrip("/").split("/")[-1] or repo
            repo_display = repo_name[:12] + "…" if len(repo_name) > 12 else repo_name
        else:
            repo_display = "[#8a8a8a]No Repo[/]"
        if branch:
            branch_display = branch[:12] + "…" if len(branch) > 12 else branch
        else:
            branch_display = "[#8a8a8a]No Branch[/]"
        status_left = f"[#8a8a8a]<>[/] {repo_display}   [#8a8a8a]⎇[/] {branch_display}   "
        self.query_one("#status-left", Static).update(status_left)

        # Sync model picker from agent (conversation or store)
        app = cast("OpenHandsApp", self.app)
        agent_model = None
        if hasattr(app, "conversation_state") and app.conversation_state:
            agent_model = app.conversation_state.agent_model
        if not agent_model:
            from openhands_cli.stores import AgentStore

            agent = AgentStore().load_or_create()
            agent_model = agent.llm.model if agent else None
        if agent_model:
            model_picker = self.query_one("#model-picker", ModelPickerSelect)
            try:
                model_picker.value = agent_model
            except ValueError:
                pass  # Model not in options, keep current
