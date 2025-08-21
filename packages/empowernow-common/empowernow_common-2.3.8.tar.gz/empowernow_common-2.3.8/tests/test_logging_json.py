import json, logging
from empowernow_common.utils.logging_config import enable_json_logging


def test_json_formatter(capsys):
    enable_json_logging(level=logging.INFO)

    logger = logging.getLogger("test")
    logger.info("hello", extra={"event": "unit_test"})

    capture = capsys.readouterr()
    raw = capture.err or capture.out
    payload = json.loads(raw.strip())
    assert payload["message"] == "hello"
    assert payload["event"] == "unit_test" 