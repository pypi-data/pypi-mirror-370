import os
import pytest
from ..config import read_configuration

EXPECTED = {
    "broker_url": "redis://localhost:6379/3",
    "result_backend": "redis://localhost:6379/4",
    "result_serializer": "pickle",
    "accept_content": ["application/json", "application/x-python-serialize"],
    "result_expires": 600,
    "task_remote_tracebacks": True,
    "broker_connection_retry_on_startup": True,
    "enable_utc": False,
    "ewoks_execution": {
        "execinfo": {
            "handlers": [
                {
                    "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
                    "arguments": [{"name": "url", "value": "redis://localhost:6379/2"}],
                }
            ]
        }
    },
}


_PY_CONTENT = """
CELERY = {
    "broker_url": "redis://localhost:6379/3",
    "result_backend": "redis://localhost:6379/4",
    "result_serializer": "pickle",
    "accept_content": ["application/json", "application/x-python-serialize"],
    "result_expires": 600,
    "task_remote_tracebacks": True,
    "broker_connection_retry_on_startup": True,
    "enable_utc": False,
}

EWOKS_EXECUTION = {
    "execinfo": {
        "handlers": [
            {
                "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
                "arguments": [{"name": "url", "value": "redis://localhost:6379/2"}],
            }
        ]
    }
}
"""

_YAML_CONTENT = """
celery:
  accept_content:
  - application/json
  - application/x-python-serialize
  broker_url: redis://localhost:6379/3
  result_backend: redis://localhost:6379/4
  result_expires: 600
  result_serializer: pickle
  task_remote_tracebacks: true
  broker_connection_retry_on_startup: true
  enable_utc: false
ewoks_execution:
  execinfo:
    handlers:
      - class: "ewoksjob.events.handlers.RedisEwoksEventHandler"
        arguments:
          - name: "url"
            value: "redis://localhost:6379/2"
"""


def test_pyfile_config(py_config: str):
    assert read_configuration(py_config) == EXPECTED
    assert read_configuration(f"file://{py_config}") == EXPECTED


def test_pymodule_config(py_config: str):
    keep = os.getcwd()
    module = os.path.splitext(os.path.basename(py_config))[0]
    os.chdir(os.path.dirname(py_config))
    try:
        assert read_configuration(module) == EXPECTED
    finally:
        os.chdir(keep)


def test_yaml_config(yaml_config: str):
    assert read_configuration(yaml_config) == EXPECTED
    assert read_configuration(f"file://{yaml_config}") == EXPECTED


def test_beacon_config(beacon_config: str):
    assert read_configuration(beacon_config) == EXPECTED


@pytest.fixture
def py_config(tmp_path) -> str:
    filename = str(tmp_path / "celeryconfig.py")
    with open(filename, "w") as f:
        f.write(_PY_CONTENT)
    return filename


@pytest.fixture
def yaml_config(tmp_path) -> str:
    filename = str(tmp_path / "ewoks.yaml")
    with open(filename, "w") as f:
        f.write(_YAML_CONTENT)
    return filename


@pytest.fixture
def beacon_config(mocker) -> str:
    url = "beacon://localhost:1234/config.yml"
    client = mocker.patch("ewoksjob.config.bliss_read_config")

    def read_config(_url):
        if _url == url:
            return EXPECTED

    client.side_effect = read_config
    return url
