"""
Pytest configuration and isolated fixtures for Windows sandbox environment.
Overrides tmp_path to avoid WinError 5 on Windows temp symlink creation.
"""
import os
import shutil
import tempfile
from pathlib import Path
import pytest


import uuid

@pytest.fixture
def tmp_path():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../results/test_tmp"))
    temp_dir = os.path.join(base_dir, f"run_{uuid.uuid4().hex[:12]}")
    os.makedirs(temp_dir, exist_ok=True)
    p = Path(temp_dir)
    yield p
    shutil.rmtree(temp_dir, ignore_errors=True)
