import pytest

from koalabyte.main import main
from koalabyte.safety import SafetyError, assert_safe_runtime


def test_self_test_runs():
    assert main(["--self-test"]) == 0


def test_runtime_requires_lab_mode(monkeypatch):
    monkeypatch.delenv("KOALABYTE_LAB_MODE", raising=False)
    with pytest.raises(SafetyError):
        assert_safe_runtime()
