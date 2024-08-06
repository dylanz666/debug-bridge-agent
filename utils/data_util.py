import os
import json
from json import JSONDecodeError

import jsonpath
from jsonpath_ng import parse


class DataUtil:
    root_path = os.getcwd()

    def __init__(self) -> None:
        pass

    @classmethod
    def get_data(cls, file_path):
        with open(os.path.join(cls.root_path, file_path), "r") as f:
            try:
                data = json.load(f)
            except JSONDecodeError:
                return {}
        return data

    @classmethod
    def get_data_by_jsonpath(cls, file_path, json_path):
        with open(os.path.join(cls.root_path, file_path), "r", encoding='utf-8') as f:
            try:
                data = json.load(f)
            except JSONDecodeError:
                return None
        try:
            return jsonpath.jsonpath(data, f"$.{json_path}")[0]
        except TypeError:
            return None

    @classmethod
    def set_data(cls, file_path, json_path, value):
        data_file_path = os.path.join(cls.root_path, file_path)
        with open(data_file_path, "r") as f:
            try:
                data = json.load(f)
            except JSONDecodeError:
                data = {}
            jsonpath_expression = parse(f"$.{json_path}")
            if len(jsonpath_expression.find(data)) == 0 and len(json_path.split(".")) > 1:
                raise ValueError(f"Could not found json path: {json_path}, please double confirm!")
            if len(jsonpath_expression.find(data)) == 0:
                data[json_path] = value
            jsonpath_expression.update(data, value)
            f.close()
        with open(data_file_path, "w") as file:
            json.dump(data, file, indent=2)
            file.close()

    @classmethod
    def write_json(cls, file_path, data):
        data_file_path = os.path.join(cls.root_path, file_path)
        with open(data_file_path, 'w') as file:
            json.dump(data, file, indent=2)
            file.close()


if __name__ == "__main__":
    pass
