# tests/conftest.py
import sys
import os
import site
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from main import app   # import absolu du FastAPI app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)