"""
Streamlit Flowsheet Component

A Streamlit component for rendering flowsheet diagrams with interactive selection.
"""

import os
import hashlib
import json
from typing import Optional, Dict, Any, List
import streamlit.components.v1 as components

# Create a _component_func which will call the frontend component.
_component_func = components.declare_component(
    "streamlit_flowsheet",
    path=os.path.join(os.path.dirname(__file__), "frontend", "build"),
)


def render_flowsheet(
    data: Dict[str, Any],
    show_navigation_panel: bool = True,
    show_properties: bool = True,
    show_border: bool = True,
    height: Optional[int] = 800,
    key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Render a flowsheet diagram with interactive selection capabilities.

    Parameters
    ----------
    data : dict
        Flowsheet data containing `simulatorObjectNodes` and `simulatorObjectEdges`
    show_navigation_panel : bool, default True
        Whether to show the left navigation panel with node hierarchy
    show_properties : bool, default True
        Whether to show the right properties panel when a node is selected
    show_border : bool, default True
        Whether to render nodes with borders
    height : int, default 800
        Height of the component in pixels
    key : str, optional
        Unique component key. If not provided, a key will be automatically generated
        based on a hash of the data content to ensure re-rendering when data changes.

    Returns
    -------
    list
        List containing the selected node (empty list if no selection).
        When a node is selected, returns [{"id": "...", "name": "...", "type": "...", "properties": [...]}]

    Examples
    --------
    >>> import streamlit as st
    >>> from streamlit_flowsheet import render_flowsheet
    >>> import json
    >>>
    >>> # Load flowsheet data
    >>> with open("example.json", "r") as f:
    ...     flowsheet_data = json.load(f)
    >>>
    >>> # Render flowsheet and get selected node
    >>> selected_node = render_flowsheet(
    ...     data=flowsheet_data,
    ...     show_navigation_panel=True,
    ...     show_properties=True,
    ...     show_border=True
    ... )
    >>>
    >>> if selected_node:
    ...     st.write(f"Selected node: {selected_node[0]['name']}")
    """

    # Generate a unique key based on data hash if no key is provided
    if key is None:
        try:
            # Create a hash of the data content
            data_str = json.dumps(data, sort_keys=True)
            data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]
            key = f"flowsheet_{data_hash}"
        except (TypeError, ValueError):
            # Fallback to a simple key if hashing fails
            key = "flowsheet_default"

    component_value = _component_func(
        data=data,
        show_navigation_panel=show_navigation_panel,
        show_properties=show_properties,
        show_border=show_border,
        height=height,
        key=key,
        default=[],
    )

    return component_value


# Make render_flowsheet available at package level
__all__ = ["render_flowsheet"]
