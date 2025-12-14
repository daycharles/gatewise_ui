# Copilot instructions — GateWise UI

Concise, actionable pointers for an AI coding assistant working on this repository.

1. Big picture

- Entry point: `main.py` calls `ui.gatewise_ui.launch_ui()` to start the PyQt5 application.
- Primary UI and logic: `ui/gatewise_ui.py` — contains all screens, persistence, and most app behavior.
- Runtime state: persisted as JSON in repository root: `users.json` and `blackout.json`.
- Hardware & network: imports `mfrc522` (RFID). Door modules are addressed via `DOOR_MODULE_IPS` and `DOOR_MODULE_PORT` constants in `ui/gatewise_ui.py`.

2. Concrete developer workflows

- Run locally (Windows/macOS/Linux desktop):

  python -m venv .venv
  .venv\Scripts\activate # Windows
  pip install -r requirements.txt
  python main.py

- On embedded hardware: install `mfrc522` and its native dependencies (not listed in `requirements.txt`); run from project root so `users.json`/`blackout.json` are created at expected locations.

3. Project-specific patterns and conventions

- UI files use `init_*` functions to build screens (e.g., `init_main_screen`, `init_user_screen`). Follow that structure when adding screens.
- Styling: colors and simple theming via `self.setStyleSheet(...)` in `GateWiseUI` — prefer small CSS strings consistent with existing colors.
- Icons/resources: loaded by path relative to the module (`resources/icons/*`). Keep image filenames and sizes consistent with existing usages.
- Persistence: JSON files live at repository root. Keep shape stable: users are objects with `uid`, `name`, `isAdmin`; blackout uses per-day arrays of {"start","end"}.

4. Integration points and missing implementations

- `push_to_door_modules()` is called from the UI (user push and auto-sync) but no implementation exists in the repo — treat it as a network-sync hook to implement (use asynchronous network calls to avoid blocking the GUI).
- `Toggle` widget is referenced but not defined in the repo. If adding a Toggle, keep its API compatible with `QCheckBox` style signals (`stateChanged`) used in `gatewise_ui.py`.
- `core/config.py` and `core/network_listener.py` are placeholders — do not assume a server or config loader exists unless added.

5. Security & testing notes

- The admin password in `request_password()` is hard-coded to "admin". Do not expose credentials in commits; replace with a configurable secret or note the change in the PR description.
- There are no automated tests in the repository currently — include small CLI-accessible sanity checks or unit tests when adding non-UI logic.

6. Helpful file references

- Launch and app structure: [main.py](main.py)
- UI + persistence: [ui/gatewise_ui.py](ui/gatewise_ui.py)
- Project dependencies: [requirements.txt](requirements.txt)
- Runtime data files: `users.json`, `blackout.json` (repo root)

If anything above is unclear or you want me to expand any section (network sync design, Toggle implementation, or adding CI/test harness), tell me which area and I will iterate.
