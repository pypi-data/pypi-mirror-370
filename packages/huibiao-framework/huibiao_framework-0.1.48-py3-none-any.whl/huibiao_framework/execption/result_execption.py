from .execption import HuiBiaoException


class TaskResultException(HuiBiaoException):
    pass


class ResultAlreadyFinishedException(TaskResultException):
    def __init__(self, folder: str):
        self.folder = folder
        super().__init__(f"Batch result already finished: {self.folder}!")
