# Streamlit Flowsheet Component

A Streamlit component for rendering interactive process flowsheet diagrams with node selection capabilities.

## Features

- Interactive process flowsheet visualization with ReactFlow
- Node selection with detailed properties panel
- Collapsible navigation panel for easy node browsing
- Theme-aware (automatically adapts to Streamlit light/dark themes)
- Configurable display options (navigation panel, properties panel, node borders)
- Returns selected node data to Streamlit

## Installation

```bash
pip install streamlit-flowsheet
```

## Usage

```python
import streamlit as st
from streamlit_flowsheet import render_flowsheet
import json

# Load model revision data (full CDF response)
with open("model_revision_data.json", "r") as f:
    full_data = json.load(f)

# Extract the flowsheet
flowsheet = full_data["items"][0]["flowsheet"]

# Render the flowsheet
selected_node = render_flowsheet(
    data=flowsheet,
    show_navigation_panel=True,
    show_properties=True,
    show_border=True,
    height=800
)

# Handle selection
if selected_node:
    st.write(f"Selected: {selected_node[0]['name']}")
```

## Parameters

- `data` (dict): Flowsheet object containing `simulatorObjectNodes` and `simulatorObjectEdges`.
- `show_navigation_panel` (bool): Show/hide the left navigation panel (default: True)
- `show_properties` (bool): Show/hide the properties panel on node selection (default: True)
- `show_border` (bool): Show/hide node borders (default: True)
- `height` (int): Component height in pixels (default: 800)

## Development

### Setup

```bash
cd streamlit-flowsheet
poetry install
cd streamlit_flowsheet/frontend
npm install
```

### Build Frontend

```bash
cd streamlit_flowsheet/frontend
npm run build
```

### Build Package

```bash
poetry build
```

## License

MIT