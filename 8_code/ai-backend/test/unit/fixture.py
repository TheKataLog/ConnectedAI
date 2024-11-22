import pytest

@pytest.fixture
def mock_outputs():
    return [
        {"user": "Hello", "AI": "How can I help you!"},
        {"user": "Hello", "AI": "How can I help you 2!"},
        {"user": "Hello", "AI": "How can I help you 3!"},
    ]