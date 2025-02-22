from pathlib import Path
import json

INIT_UTILS = {"ignore": []}


class Utils:
    def __init__(self, data_dir: Path):
        self.path: Path = data_dir / "utils.json"
        self.data: dict = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            with open(self.path, "r") as f:
                return json.load(f)
        else:
            return self.create()

    def read(self) -> dict:
        return self.data

    def update(self, field: str, new_data: list) -> None:
        if field not in self.data:
            self.data[field] = []
        self.data[field].extend(new_data)
        self.data[field] = sorted(list(set(self.data[field])))
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def create(self) -> dict:
        with open(self.path, "w") as f:
            json.dump(INIT_UTILS, f, indent=4)
        return INIT_UTILS

    def __str__(self):
        str_return = ""
        for key, value in self.read().items():
            str_return += f"{key}: {value}\n"

        return str_return
