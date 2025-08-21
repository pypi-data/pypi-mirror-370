# © Copyright 2024-2025 Hewlett Packard Enterprise Development LP
import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_login() -> None:
    print("\nDoing setup")
    os.environ["AIOLI_USER_TOKEN"] = "test-token"
