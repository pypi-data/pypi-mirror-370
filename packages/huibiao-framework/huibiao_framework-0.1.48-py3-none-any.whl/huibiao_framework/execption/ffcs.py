from .execption import HuiBiaoException


class FfcsClientError(HuiBiaoException):
    pass


class FfcsSendProgressError(FfcsClientError):
    def __init__(self, reason, e: Exception = None, reqid: str = None):
        self.reason = reason
        self.e = e
        self.reqid = reqid
        super().__init__(f"发送进度失败,reqid={self.reqid},原因：{self.reason}")
