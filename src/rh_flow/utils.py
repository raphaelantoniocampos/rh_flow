from pathlib import Path
import json

INIT_UTILS = {"ignore": {}}


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

    def update(self, field: str, new_data: dict) -> None:
        if field not in self.data:
            self.data[field] = {}

        self.data[field].update(new_data)

        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def create(self) -> dict:
        with open(self.path, "w") as f:
            json.dump(INIT_UTILS, f, indent=4)
        return INIT_UTILS

    def remove(self, field: str, key: str) -> str:
        if field in self.data and key in self.data[field]:
            del self.data[field][key]
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=4)
            return f"Item '{key}' removido do campo '{field}'."
        else:
            return f"Item '{key}' não encontrado no campo '{field}'."

    def __str__(self):
        str_return = ""
        for key, value in self.read().items():
            str_return += f"{key}: {value}\n"

        return str_return
