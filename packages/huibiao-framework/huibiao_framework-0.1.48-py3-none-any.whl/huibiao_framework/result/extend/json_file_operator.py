import json
from typing import Dict

from huibiao_framework.result.result import FileOperator


class JsonOperator(FileOperator[Dict]):
    @classmethod
    def file_suffix(cls) -> str:
        return "json"

    @classmethod
    def load(cls, path: str, **kwargs) -> Dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def save(cls, data: Dict, path, **kwargs):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
