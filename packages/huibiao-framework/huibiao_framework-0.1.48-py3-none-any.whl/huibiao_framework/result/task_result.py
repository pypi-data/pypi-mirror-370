import os
from typing import Dict, Type, TypeVar

from huibiao_framework.config import TaskConfig
from huibiao_framework.utils.annotation import frozen_attrs
from . import FileOperator
from .extend import JsonOperator

from .result import BatchResult, Result, SingleResult

F = TypeVar("F", bound=FileOperator)
R = TypeVar("R", bound=Result)
D = TypeVar("D")


@frozen_attrs("task_dir", "task_type", "task_id", "resource_dict")
class TaskResult:
    def __init__(self, task_type: str, task_id: str):
        self.task_dir = os.path.join(
            TaskConfig.TASK_RESOURCE_DIR, str(task_type), str(task_id)
        )
        self.task_id = task_id
        self.task_type = task_type
        self.__resource_dict: Dict[str, R] = {}

    def __getitem__(self, item) -> R | None:
        if item in self.result_dict:
            return self.result_dict[item]
        else:
            return None

    @property
    def result_dict(self) -> dict[str, R]:
        return self.__resource_dict

    def addResult(self, name: str, operator: type[F]) -> SingleResult[F, D]:
        """
        name是文件名，不需要带”。***“后缀
        """
        res = SingleResult(
            operator=operator,
            path=os.path.join(self.task_dir, f"{name}.{operator.file_suffix()}"),
        )
        self.result_dict[name] = res
        return res

    def addBatchResult(self, name: str, operator: Type[F]) -> BatchResult[F, D]:
        """
        name是目录名，也是结果名
        """
        res = BatchResult(operator=operator, folder=os.path.join(self.task_dir, name))
        self.result_dict[name] = res
        return operator

    def load(self):
        for _, r in self.result_dict.items():
            r.load()

    def save(self):
        for _, r in self.result_dict.items():
            r.save()

    def addJsonResult(
        self,
        name: str,
    ) -> SingleResult[JsonOperator, Dict]:
        return self.addResult(name=name, operator=JsonOperator)

