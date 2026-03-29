"""
tests/test_app.py
-----------------
Pytest test suite for the Dash app.

Run:
    pytest -v

Requires:
    pip install "dash[testing]" pytest
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app


# ── Fixture ─────────────────────────────────────────────

@pytest.fixture
def dash_app(dash_duo):
    dash_duo.start_server(app)
    dash_duo.wait_for_element("h1", timeout=10)
    return dash_duo


# ── Tests ───────────────────────────────────────────────

def test_header_present(dash_app):
    """Test: Header exists"""
    header = dash_app.find_element("h1")
    assert header is not None
    assert "Pink Morsel Sales" in header.text


def test_graph_present(dash_app):
    """Test: Graph exists"""
    graph = dash_app.find_element("#sales-graph")
    assert graph is not None

    # Check Plotly rendered inside
    dash_app.wait_for_element("#sales-graph .js-plotly-plot", timeout=10)


def test_region_picker_present(dash_app):
    """Test: Region radio exists"""
    radio = dash_app.find_element("#region-filter")
    assert radio is not None

    # Check number of options
    options = dash_app.driver.find_elements(
        "css selector", "#region-filter input[type='radio']"
    )
    assert len(options) == 5


def test_region_labels_correct(dash_app):
    """Test: Correct region labels"""
    labels = dash_app.driver.find_elements(
        "css selector", "#region-filter label"
    )

    expected = {"All", "North", "East", "South", "West"}
    actual = {label.text.strip() for label in labels}

    assert actual == expected