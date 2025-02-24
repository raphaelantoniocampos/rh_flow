import pytest
import json
from pathlib import Path
from rh_flow.config import Config, INIT_CONFIG


@pytest.fixture
def temp_dir():
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_create(temp_dir):
    config = Config(temp_dir)

    assert config.path.exists()

    with open(config.path, "r") as f:
        content = json.load(f)
    assert content == INIT_CONFIG


def test_read(temp_dir):
    config = Config(temp_dir)

    assert config.read() == INIT_CONFIG


def test_update(temp_dir):
    config = Config(temp_dir)

    config._update("ignore", ["funcionario1", "funcionario2"])

    with open(config.path, "r") as f:
        content = json.load(f)
    assert content == {"ignore": ["funcionario1", "funcionario2"]}

    config._update("ignore", ["funcionario3"])
    with open(config.path, "r") as f:
        content = json.load(f)
    assert content == {"ignore": ["funcionario1", "funcionario2", "funcionario3"]}


def test_update_with_empty_ignore(temp_dir):
    config = Config(temp_dir)

    config.data.pop("ignore", None)
    with open(config.path, "w") as f:
        json.dump(config.data, f, indent=4)

    config._update("ignore", ["funcionario1"])

    with open(config.path, "r") as f:
        content = json.load(f)
    assert content == {"ignore": ["funcionario1"]}
