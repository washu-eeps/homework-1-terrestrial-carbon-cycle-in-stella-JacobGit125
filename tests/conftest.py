"""Pytest configuration for HW1 autograder."""

import pytest


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "base_model: tests for base model structure"
    )
    config.addinivalue_line(
        "markers", "calibration: tests for calibration"
    )
    config.addinivalue_line(
        "markers", "feedback: tests for feedback mechanism"
    )
    config.addinivalue_line(
        "markers", "scenarios: tests for scenario design"
    )
    config.addinivalue_line(
        "markers", "mass_conservation: tests for mass conservation"
    )
