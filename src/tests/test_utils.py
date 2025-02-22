import pytest
import json
from pathlib import Path
from rh_flow.utils import Utils, INIT_UTILS


@pytest.fixture
def temp_dir():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_create(temp_dir):
    utils = Utils(temp_dir)

    assert utils.path.exists()

    with open(utils.path, "r") as f:
        content = json.load(f)
    assert content == INIT_UTILS


def test_read(temp_dir):
    utils = Utils(temp_dir)

    assert utils.read() == INIT_UTILS


def test_update(temp_dir):
    utils = Utils(temp_dir)

    utils.update("ignore", ["funcionario1", "funcionario2"])

    with open(utils.path, "r") as f:
        content = json.load(f)
    assert content == {"ignore": ["funcionario1", "funcionario2"]}

    utils.update("ignore", ["funcionario3"])
    with open(utils.path, "r") as f:
        content = json.load(f)
    assert content == {"ignore": ["funcionario1", "funcionario2", "funcionario3"]}


def test_update_with_empty_ignore(temp_dir):
    utils = Utils(temp_dir)

    utils.data.pop("ignore", None)
    with open(utils.path, "w") as f:
        json.dump(utils.data, f, indent=4)

    utils.update("ignore", ["funcionario1"])

    with open(utils.path, "r") as f:
        content = json.load(f)
    assert content == {"ignore": ["funcionario1"]}
