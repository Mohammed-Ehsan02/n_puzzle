# conftest.py — pytest configuration
# Adds src/ to Python's module search path so tests can import from src/
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
