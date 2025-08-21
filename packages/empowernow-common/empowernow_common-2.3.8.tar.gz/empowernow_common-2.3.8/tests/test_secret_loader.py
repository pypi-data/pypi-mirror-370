import os
import tempfile
from pathlib import Path

import pytest

import importlib

# Import only the secret_loader submodule to avoid heavy package-level deps
secret_mod = importlib.import_module("empowernow_common.secret_loader")
load_secret = secret_mod.load_secret  # type: ignore[attr-defined]
SecretNotFound = secret_mod.SecretNotFound  # type: ignore[attr-defined]


def test_env_provider(monkeypatch):
    monkeypatch.setenv("MY_API_KEY", "12345")
    assert load_secret("env:MY_API_KEY") == "12345"


def test_env_provider_missing(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    with pytest.raises(SecretNotFound):
        load_secret("env:MISSING_VAR")


def test_file_provider(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        # create file path /tmp/primary/secret1
        secret_dir = Path(tmp) / "primary"
        secret_dir.mkdir(parents=True)
        (secret_dir / "secret1").write_text("super-secret\n", encoding="utf-8")

        monkeypatch.setenv("FILE_MOUNT_PATH", tmp)
        assert load_secret("file:primary:secret1") == "super-secret"


def test_file_provider_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("FILE_MOUNT_PATH", str(tmp_path))
    with pytest.raises(SecretNotFound):
        load_secret("file:primary:does_not_exist") 


def test_filex_provider_dict(monkeypatch, tmp_path):
    secret_dir = tmp_path / "primary"
    secret_dir.mkdir(parents=True)
    (secret_dir / "dbcreds").write_text("username=admin\npassword=secret", encoding="utf-8")
    monkeypatch.setenv("FILE_MOUNT_PATH", str(tmp_path))
    value = load_secret("filex:primary:dbcreds")
    assert isinstance(value, dict)
    assert value["password"] == "secret" 