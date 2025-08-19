import faiss

from huibiao_framework.result.result import FileOperator


class FaissOperator(FileOperator[faiss.Index]):
    @classmethod
    def file_suffix(cls) -> str:
        return "index"

    @classmethod
    def load(cls, path: str, **kwargs) -> faiss.Index:
        return faiss.read_index(path)

    @classmethod
    def save(cls, data: faiss.Index, path, **kwargs):
        faiss.write_index(data, path)
