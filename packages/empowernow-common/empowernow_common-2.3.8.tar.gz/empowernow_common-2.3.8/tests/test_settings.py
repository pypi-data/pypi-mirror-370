import os
from pathlib import Path

import pytest

from empowernow_common.settings import EmpowerNowSettings


def test_settings_precedence(tmp_path, monkeypatch):
    # YAML file sets async_logging = false
    yaml_path = tmp_path / "settings.yaml"
    yaml_path.write_text("""async_logging: false
log_json_default: false
""")

    # Env var overrides log_json_default
    monkeypatch.setenv("LOG_JSON", "1")

    # Explicit kwarg overrides async_logging
    settings = EmpowerNowSettings.load(yaml_path=yaml_path, async_logging=True)

    assert settings.async_logging is True  # kwarg beats YAML
    assert settings.log_json_default is False  # YAML overrides env in precedence 