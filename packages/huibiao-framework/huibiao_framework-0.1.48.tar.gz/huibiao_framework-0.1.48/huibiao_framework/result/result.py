import os
import time
from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar, final, Dict, Type

from huibiao_framework.execption.result_execption import ResultAlreadyFinishedException
from huibiao_framework.utils.meta_class import ConstantClass


class ResultStatusTagConstant(ConstantClass):
    DONE = "__DONE"


D = TypeVar("D")


# region 文件操作抽象类
class FileOperator(Generic[D], ABC):
    """
    文件操作抽象类
    """

    @classmethod
    @abstractmethod
    def file_suffix(cls) -> str:
        """子类必须实现此类方法，对丁文件的后缀名，不能包含点"""
        pass

    @classmethod
    @abstractmethod
    def load(cls, path: str, **kwargs) -> D:
        """
        从本地加载文件
        """
        pass

    @classmethod
    @abstractmethod
    def save(cls, data: D, path, **kwargs):
        """
        保存文件到本地
        """
        pass


# endregion

F = TypeVar("F", bound=FileOperator)


# region 抽象结果类
class Result(Generic[F, D], ABC):
    def __init__(self, operator: Type[F]):
        self.__operator: Type[F] = operator

    @abstractmethod
    def is_completed(self, *args, **kwargs) -> bool:
        """
        该资源是否准备完毕
        """
        pass

    @abstractmethod
    def complete(self):
        pass

    @property
    def operator(self) -> F:
        return self.__operator

    @abstractmethod
    def load(self, **kwargs):
        pass

    @abstractmethod
    def save(self, **kwargs):
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    def __repr__(self):
        return self.description()

    def __str__(self):
        return self.description()


# endregion


# region 单个文件结果类
class SingleResult(Result[F, D]):
    def __init__(self, path: str, operator: Type[F] = None):
        super().__init__(operator)
        self.__path = path
        self.__data = None

    @property
    def data(self) -> D:
        return self.__data

    @final
    def is_completed(self) -> bool:
        return os.path.exists(self.__path)

    @final
    def complete(self):
        if not self.is_completed():
            self.save()

    def load(self, **kwargs):
        if os.path.exists(self.__path):
            self.__data = self.operator.load(path=self.__path, **kwargs)

    def save(self, **kwargs):
        if self.__data is not None:
            os.makedirs(os.path.dirname(self.__path), exist_ok=True)
            self.operator.save(path=self.__path, data=self.__data, **kwargs)

    @property
    def path(self) -> str:
        return self.__path

    def description(self) -> str:
        return f"{self.operator.__class__.__name__}[{self.operator.path}]"


# endregion


# region 多个文件结果类
class BatchResult(Result[F, D]):
    def __init__(self, folder: str, operator: Type[F]):
        super().__init__(operator)
        self.__folder = folder
        self.__data: Dict[int, D] = {}
        os.makedirs(self.folder, exist_ok=True)
        self.complete_tag_path = os.path.join(
            self.folder, ResultStatusTagConstant.DONE
        )


    def __getitem__(self, idx) -> F:
        return self.__data[idx]

    def __len__(self):
        return len(self.__data)

    @property
    def folder(self) -> str:
        return self.__folder

    def load(self, **kwargs):
        for path in self.path:
            idx = int(os.path.basename(path).split(".")[0])
            self.__data[idx] = self.operator.load(path=path)

    def save(self, **kwargs):
        for idx, data in self.__data.items():
            self.operator.save(
                path=self.genPath(idx),
                data=data,
                **kwargs,
            )

    def genPath(self, idx: int):
        return os.path.join(self.folder, f"{str(idx)}.{self.operator.file_suffix()}")

    @final
    def is_completed(self) -> bool:
        return os.path.exists(self.complete_tag_path)

    def append(self, data: D):
        if self.is_completed():
            raise ResultAlreadyFinishedException(
                folder=self.folder
            )
        idx = len(self) + 1
        self.__data[idx] = data

    @final
    def complete(self):
        if os.path.exists(self.complete_tag_path):
            return  # 忽略该操作
        with open(
            self.complete_tag_path,
            "w",
        ) as f:
            local_time = time.localtime(time.time())
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            f.write(formatted_time)  # 往目录下写入一个文件，包含当前时间

    @property
    def path(self) -> List[str]:
        return [
            os.path.join(self.folder, r)
            for r in os.listdir(self.folder)
            if r != ResultStatusTagConstant.DONE
        ]

    def description(self) -> str:
        return f"{self.operator.__class__.__name__}[{self.operator.folder}]"


# endregion
