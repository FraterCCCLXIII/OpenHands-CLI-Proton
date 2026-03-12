---
name: prototype-to-cli-migration
description: Migrate UI components from the OpenHands prototype into the production CLI. Use when the user asks to migrate, port, or import a component from prototype to the CLI, or when moving UI elements from prototype/openhands_cli.py into openhands_cli/tui/.
---

# Prototype-to-CLI Migration

When migrating a UI component from `prototype/openhands_cli.py` to the production CLI, follow the **extract-first** workflow. Production never imports from prototype.

## Workflow

1. **Identify the component** — Locate the class in `prototype/openhands_cli.py` (e.g. `CheckmarkSelectOverlay`, `LLMProfileModalScreen`, `ChangesPanel`).

2. **Choose the target module**:
   | Component type | Target path |
   |----------------|-------------|
   | Widgets (Select overlays, custom inputs) | `openhands_cli/tui/widgets/` |
   | Modal screens | `openhands_cli/tui/modals/` |
   | Panels (ChangesPanel, ProfileManagerPanel) | `openhands_cli/tui/panels/` |
   | Dataclasses (ChatMessage, TodoItem, ChangedFile) | `openhands_cli/tui/widgets/` or `openhands_cli/tui/core/` |

3. **Extract** — Create a new file in the target module and copy the class. Fix imports to use `textual`, `rich`, etc. directly. Remove any prototype-specific dependencies.

4. **Export** — Add the component to the module's `__init__.py` and `__all__`.

5. **Update prototype** — Replace the class definition in `prototype/openhands_cli.py` with:
   ```python
   from openhands_cli.tui.widgets.<module> import ComponentName
   ```
   (Adjust path for modals/panels.)

6. **Wire in production** — Add the component to the production app's compose tree or the appropriate screen. Replace mock data with real data from `ConversationManager`, `ConversationContainer`, or services.

7. **Copy CSS** — Copy relevant selectors from `prototype/openhands_cli.tcss` into `openhands_cli/tui/textual_app.tcss` (or panel-specific `.tcss`).

## Dependency order

If component A depends on component B, port B first. Example: `ModelPickerSelect` depends on `CheckmarkSelectOverlay` → port `CheckmarkSelectOverlay` first.

## Rules

- **Production never imports from prototype**
- **Prototype may import from production** for ported components
- Keep a single source of truth: once ported, the component lives in `openhands_cli`

## Reference

For dummy flows, service abstractions, and detailed porting steps, see `prototype/MIGRATION.md`.
