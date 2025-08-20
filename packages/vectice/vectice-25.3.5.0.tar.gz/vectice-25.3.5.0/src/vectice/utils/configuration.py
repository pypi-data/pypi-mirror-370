from __future__ import annotations

import json
from json import JSONDecodeError


class Configuration:
    def __init__(self, config_file_path: str):
        with open(config_file_path, "r") as config_file:
            try:
                self.config_object = json.load(config_file)
            except JSONDecodeError as error:
                raise SyntaxError("Can not read JSON config file. Check that the file structure is valid.") from error

    def __getitem__(self, key: str) -> str:
        information: str = self.config_object.get(key)
        if not information:
            raise KeyError(f"Error while reading the configuration, {key} is empty.")
        return information
