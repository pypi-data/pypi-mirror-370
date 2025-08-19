# routelit-mantine

[![Release](https://img.shields.io/github/v/release/routelit/routelit-mantine)](https://img.shields.io/github/v/release/routelit/routelit-mantine)
[![Build status](https://img.shields.io/github/actions/workflow/status/routelit/routelit-mantine/main.yml?branch=main)](https://github.com/routelit/routelit-mantine/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/routelit/routelit-mantine/branch/main/graph/badge.svg)](https://codecov.io/gh/routelit/routelit-mantine)
[![Commit activity](https://img.shields.io/github/commit-activity/m/routelit/routelit-mantine)](https://img.shields.io/github/commit-activity/m/routelit/routelit-mantine)
[![License](https://img.shields.io/github/license/routelit/routelit-mantine)](https://img.shields.io/github/license/routelit/routelit-mantine)


This is a routelit library that provides a Python builder API that maps to a React client powered by Mantine components. You describe UI declaratively in Python; RouteLit streams diffs to the browser where Mantine renders beautiful, accessible components.

- **Github repository**: <https://github.com/routelit/routelit-mantine/>
- **Documentation** <https://routelit.github.io/routelit-mantine/>

## Features

- Rich Mantine components exposed in Python
  - Inputs: checkbox, chip, text input, number input, password input, selects, tags, sliders, rating, switches, groups
  - Layouts: container, grid, flex, group, stack, simple grid, space, app shell, scroll areas, paper/box
  - Navigation: anchors, tabs, nav links, sidebar
  - Feedback and overlays: alerts, notifications, dialogs, drawers, affix, spoiler
  - Data display and charts: tables, images, formatters, area/line/bar/pie/donut/radar/scatter/bubble/radial bar/sparkline/heatmap
- Server-driven model with a clean builder `RLBuilder`
- Flask adapter for easy integration (`routelit-flask`)

## Getting started with your project

to install the library, run:

```bash
pip install routelit-mantine
# or
uv add routelit-mantine
```

### Quickstart (Flask)

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


### License

Apache 2.0

---
Author: [rolangom](https://x.com/rolangom)

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
