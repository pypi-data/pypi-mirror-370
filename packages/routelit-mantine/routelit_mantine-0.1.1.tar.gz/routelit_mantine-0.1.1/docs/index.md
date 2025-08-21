# routelit-mantine

Build Mantine-based, server‑driven UIs in Python with RouteLit.

`routelit-mantine` provides a Python builder API that maps to a React client powered by Mantine components. You describe UI declaratively in Python; RouteLit streams diffs to the browser where Mantine renders beautiful, accessible components.

— Python ≥ 3.9 —

## Features

- Rich Mantine components exposed in Python
  - Inputs: checkbox, chip, text input, number input, password input, selects, tags, sliders, rating, switches, groups
  - Layouts: container, grid, flex, group, stack, simple grid, space, app shell, scroll areas, paper/box
  - Navigation: anchors, tabs, nav links, sidebar
  - Feedback and overlays: alerts, notifications, dialogs, drawers, affix, spoiler
  - Data display and charts: tables, images, formatters, area/line/bar/pie/donut/radar/scatter/bubble/radial bar/sparkline/heatmap
- Server-driven model with a clean builder `RLBuilder`
- Flask adapter for easy integration (`routelit-flask`)
- Great DX: hot dev server for components via Vite

## Installation

Install the library from PyPI:

```bash
pip install routelit-mantine
```

If you are building a Flask app, also install the adapter and Flask:

```bash
pip install routelit-flask flask
```

## Quickstart (Flask)

```python
from flask import Flask, Response
from routelit import RouteLit
from routelit_flask import RouteLitFlaskAdapter
from routelit_mantine import RLBuilder

app = Flask(__name__)

rl = RouteLit(BuilderClass=RLBuilder)
adapter = RouteLitFlaskAdapter(rl).configure(app)

def index_view(ui: RLBuilder) -> None:
    ui.set_page_config(page_title="Home")
    ui.title("Mantine RouteLit")
    ui.text("Hello from Python 👋")
    if ui.button("Click me"):
        ui.notification("Clicked!", color="green")

@app.route("/", methods=["GET", "POST"])
def index() -> Response:
    return adapter.stream_response(index_view)

if __name__ == "__main__":
    app.run(debug=True)
```

Open your browser at `http://127.0.0.1:5000/`.

### Developing with the local component dev server

Run the React component playground locally for fast iterations:

```bash
cd src/frontend
pnpm install
pnpm run dev
```

Then start your Python server and point RouteLit to the local dev server:

```python
from routelit_flask import RouteLitFlaskAdapter
adapter = RouteLitFlaskAdapter(
    rl,
    run_mode="dev_components",
    local_components_server="http://localhost:5173",
).configure(app)
```

## Run the example in this repo

This repository ships with a comprehensive demo showcasing most components.

1) Start the frontend dev server:

```bash
cd src/frontend
pnpm install
pnpm run dev
```

2) In another terminal, sync Python deps and run the example app:

```bash
uv sync
uv run src/example/example.py
```

Visit `http://127.0.0.1:5000/` and explore the pages (Layouts, Inputs, Combobox, Buttons, Navigation, Feedback, Overlays, Charts, Dates, etc.).

## Key concepts

- Builder (`RLBuilder`): the Python API that describes UI (e.g., `ui.button`, `ui.grid`, `ui.dialog`).
- Views and fragments: plain Python callables that receive `RLBuilder` and compose UI.
- Overlays: dialogs and drawers can be created inline or via decorators.
- App shell and sidebar: use `ui.set_app_shell_props` and navigate with `ui.nav_link`.
- Stateful interactions: use `ui.session_state` and `ui.rerun()` to manage state and trigger updates.

## Configuration notes

- Flask adapter options:
  - `run_mode`: `prod` (default), `dev_components` or `dev_client`
  - `local_components_server`: point to the Vite dev server (e.g., `http://localhost:5173`)

## Links

- Source code: https://github.com/routelit/routelit-mantine
- PyPI: https://pypi.org/project/routelit-mantine/
- API Reference: see Modules in the left nav or open [`modules.md`](modules.md)

## License

APACHE 2.0 — see the LICENSE file in the repository.
