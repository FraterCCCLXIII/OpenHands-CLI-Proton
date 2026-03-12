# Prototype Migration Guide

How to port UI changes from the prototype to the OpenHands CLI, and how to add dummy UX flows where functionality doesn't exist yet.

---

## Running the Prototype vs Production

| Command | What it runs |
|---------|--------------|
| `openhands` | Production TUI (real OpenHands SDK, conversations, agents) |
| `openhands prototype` | Prototype TUI (experimental screens, dummy data, mock flows) |

The prototype is self-contained in `prototype/openhands_cli.py` and `openhands_cli.tcss`. It uses **mock data only**—no real agent, no real conversations. Use it to:

- Iterate on new UI designs
- Test layouts and interactions before wiring to real backend
- Demo flows to stakeholders before implementation

---

## How to Import UI Elements from Prototype into the CLI

**Use the extract-first workflow.** Don't import from prototype into production at runtime. Instead:

1. **Extract** the component from prototype into the CLI
2. **Refactor** prototype to import from the CLI for that component
3. **Wire** the component in production to real data

### Step-by-step: Porting a component

**Example: Port `CheckmarkSelectOverlay`**

1. **Create a new file** in the CLI for the component:
   ```
   openhands_cli/tui/widgets/checkmark_select.py
   ```

2. **Copy the class** from `prototype/openhands_cli.py` into that file. Fix imports to use `textual` and `rich` directly (no prototype imports).

3. **Export it** from `openhands_cli/tui/widgets/__init__.py`:
   ```python
   from openhands_cli.tui.widgets.checkmark_select import CheckmarkSelectOverlay
   __all__ = [..., "CheckmarkSelectOverlay"]
   ```

4. **Update the prototype** to import from the CLI instead of defining it locally:
   ```python
   # In prototype/openhands_cli.py - replace the class definition with:
   from openhands_cli.tui.widgets.checkmark_select import CheckmarkSelectOverlay
   ```

5. **Use it in production** wherever needed:
   ```python
   from openhands_cli.tui.widgets import CheckmarkSelectOverlay
   ```

6. **Copy related CSS** from `prototype/openhands_cli.tcss` into `openhands_cli/tui/textual_app.tcss`.

### Where to put components

| Prototype class | Production target |
|-----------------|-------------------|
| `CheckmarkSelectOverlay`, `ModelPickerSelect` | `openhands_cli/tui/widgets/` |
| `ModalDialogScreen`, `LLMProfileModalScreen` | `openhands_cli/tui/modals/` |
| `ChangesPanel`, `ProfileManagerPanel` | `openhands_cli/tui/panels/` |
| Dataclasses (`ChatMessage`, `TodoItem`) | `openhands_cli/tui/widgets/` or `openhands_cli/tui/core/` |

### Dependency direction

- **Production never imports from prototype** — keeps the CLI stable.
- **Prototype may import from production** — for components that have been ported. Once a component lives in `openhands_cli/tui/`, both use it.

### Handling dependencies

If a component depends on others (e.g. `ModelPickerSelect` → `CheckmarkSelectOverlay`), port the base components first.

---

## Strategy 1: Port UI Incrementally

### Recommended flow

1. **Design in prototype** → Build new screens, modals, or components in `prototype/openhands_cli.py`.
2. **Validate UX** → Run `openhands prototype` and test with dummy data.
3. **Extract & port** → Move validated pieces into production modules under `openhands_cli/tui/`.

### What to port

| Prototype area | Production target |
|----------------|-------------------|
| Custom widgets (e.g. `CheckmarkSelectOverlay`) | `openhands_cli/tui/widgets/` |
| Modal screens (e.g. `LLMProfileModalScreen`) | `openhands_cli/tui/modals/` |
| Panel layouts (thread list, chat view) | `openhands_cli/tui/panels/` |
| CSS styles | `openhands_cli/tui/textual_app.tcss` or panel-specific `.tcss` |

### Porting steps

1. Copy the widget/screen class into the appropriate production module.
2. Fix imports (e.g. `from openhands_cli.tui.widgets...`).
3. Replace mock data with real data from `ConversationManager`, `ConversationContainer`, or other services.
4. Add the component to the production app’s compose tree.
5. Copy relevant CSS from `prototype/openhands_cli.tcss` into production stylesheets.

---

## Strategy 2: Dummy UX Flows

Use dummy flows when the backend or feature isn’t ready yet.

### Pattern A: Mock data in prototype (current approach)

The prototype already uses this pattern:

```python
def _build_seed_changes(self) -> list[ChangedFile]:
    """Return fake changed files for /changes demo."""
    return [
        ChangedFile(path="src/styles/global.css", additions=2, deletions=1, ...),
        ...
    ]

def _build_seed_todos(self) -> list[TodoItem]:
    """Return fake todos for plan/task demo."""
    return [
        TodoItem(title="Convert search bar...", status="done", ...),
        ...
    ]
```

Add new dummy flows by:

1. Defining a dataclass for the flow’s data (e.g. `ProfileItem`, `CloudWorkspace`).
2. Implementing a `_build_seed_*()` method that returns fake instances.
3. Wiring the UI to that method instead of a real service.

### Pattern B: Service abstraction (for production)

When porting to production, introduce an abstraction so you can swap real vs mock:

```python
# openhands_cli/tui/services/profile_service.py
from abc import ABC, abstractmethod

class ProfileService(ABC):
    @abstractmethod
    def list_profiles(self) -> list[Profile]: ...

    @abstractmethod
    def get_active(self) -> Profile | None: ...

class RealProfileService(ProfileService):
    """Wired to real agent_settings.json, etc."""
    ...

class MockProfileService(ProfileService):
    """Returns dummy data for UI development."""
    def list_profiles(self) -> list[Profile]:
        return [Profile(name="Demo", model="gpt-4", ...)]
```

Then inject the implementation based on a flag or environment:

```python
# In app init or factory
profile_service = MockProfileService() if demo_mode else RealProfileService()
```

### Pattern C: Slash commands as demo entry points

The prototype uses slash commands to trigger demo flows:

- `/changes` → Shows mock changed files with expandable diffs
- `/profile2` → Profile manager with fake profiles
- `/modal` → Generic modal dialog
- `/sample` → Multiline prompt + approval selection

Add new dummy flows by:

1. Adding a `SlashCommand` in the prototype’s command list.
2. Implementing a handler that pushes a screen or updates state with mock data.
3. Reusing existing mock helpers (`_build_seed_*`) where possible.

---

## Quick Reference: Adding a New Dummy Flow

1. **In prototype** (`prototype/openhands_cli.py`):
   - Add a `SlashCommand("myflow", "Description")` to the slash menu.
   - Add a handler (e.g. `_handle_myflow`) that sets state or pushes a screen.
   - Add `_build_seed_myflow_data()` returning fake data.
   - Wire the UI to `_build_seed_myflow_data()`.

2. **When porting to production**:
   - Create a service interface (e.g. `MyFlowService`) with real and mock implementations.
   - Use the real implementation by default; use mock when `--demo` or similar is set.
   - Port the UI component and connect it to the service.

---

## File Layout

```
openhands-cli-proton/
├── prototype/                    # UI experiments, always uses mocks
│   ├── openhands_cli.py          # Main prototype app
│   ├── openhands_cli.tcss        # Prototype styles
│   ├── README.md
│   └── MIGRATION.md             # This file
│
└── openhands_cli/
    └── tui/                      # Production TUI
        ├── textual_app.py       # Main production app
        ├── textual_app.tcss     # Production styles
        ├── core/                # ConversationManager, state, etc.
        ├── modals/              # Modal screens
        ├── panels/              # Side panels
        └── widgets/             # Reusable widgets
```

---

## Tips

- **Extract, don't import** — Production never imports from prototype. When porting, move the component into `openhands_cli` first; then prototype can import it from there for a single source of truth.
- **Sync styles when porting** — Copy CSS from prototype to production and adjust selectors if the DOM structure changes.
- **Use the same design tokens** — Share colors, spacing, and typography between prototype and production for consistency.
- **Document mock data shape** — Match your `_build_seed_*` return types to the real API/data models you plan to use later.
