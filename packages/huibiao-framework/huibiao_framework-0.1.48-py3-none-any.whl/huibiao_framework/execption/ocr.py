from .execption import HuiBiaoException


class ImageOcrResponseCodeError(HuiBiaoException):
    def __init__(self, code: int):
        self.code = code
        super().__init__(f"OCR模型处理失败，code={self.code}!")


class ImageOcrResponseFormatError(HuiBiaoException):
    def __init__(self, item: str):
        self.error_item = item
        super().__init__(f"ImageOcr模型返回结果格式错误，错误字段{self.error_item}")


class LayoutDetectionResponseCodeError(HuiBiaoException):
    def __init__(self, code: int):
        self.code = code
        super().__init__(f"LayoutDetection模型处理失败，code={self.code}!")


class LayoutDetectionResponseFormatError(HuiBiaoException):
    def __init__(self, item: str):
        self.error_item = item
        super().__init__(
            f"LayoutDetection模型返回结果格式错误，错误字段{self.error_item}"
        )


class ConvertToPdfResponseCodeError(HuiBiaoException):
    def __init__(self, code: int):
        self.code = code
        super().__init__(f"ConvertToPdf模型处理失败，code={self.code}!")


class ConvertToPdfResponseFormatError(HuiBiaoException):
    def __init__(self, item: str):
        self.error_item = item
        super().__init__(f"ConvertToPdf模型返回结果格式错误，错误字段{self.error_item}")


class DocumentParseResponseCodeError(HuiBiaoException):
    def __init__(self, code: int):
        self.code = code
        super().__init__(f"FileParse模型处理失败，code={self.code}!")


class DocumentParseResponseFormatError(HuiBiaoException):
    def __init__(self, item: str):
        self.error_item = item
        super().__init__(f"FileParse模型返回结果格式错误，错误字段{self.error_item}")
