from typing import TypeVar

from loguru import logger

from huibiao_framework.client import MinIOClient
from huibiao_framework.config import MinioConfig
from huibiao_framework.execption.minio import MinioClientConnectException
from huibiao_framework.result import (
    TaskResult,
)

# SF = TypeVar("SF", bound=FileResource)
# BF = TypeVar("BF", bound=BatchFileResource)


class TaskResourceSyncMinio:
    """
    将一个算法任务的中间结果上传到minio或下载到本地
    任务资源本地目录 <<=>> object_name_base
    """

    def __init__(
        self,
        *,
        task_result: TaskResult,
        bucket_name: str = None,
    ):
        if task_result is None:
            raise ValueError("Task result cant not be None")
        self._task_resource = task_result
        self._object_name_base = (
            f"task_resource/{task_result.task_type}/{task_result.task_id}/"
        )
        self._bucket_name = bucket_name if bucket_name else MinioConfig.BUCKET_NAME
        self._minio_client = MinIOClient()
        self.enabled = False

    async def init(self):
        try:
            await self._minio_client.init()
            self.enabled = True
        except MinioClientConnectException:
            logger.info("Minio连接失败,无法同步任务中间结果")

    async def close(self):
        await self._minio_client.close()

    async def upload_all(self):
        """
        把一个算法任务的中间结果上传到minio
        """
        if self.enabled:
            pass  # todo

    async def download_all(self):
        """
        从minio下载算法任务的中间结果
        """
        if self.enabled:
            pass  # todo

    async def upload_file(self, resource_name: str, resource):
        if self.enabled:
            pass  # todo

    async def upload_batch_file(self, local_dir):
        if self.enabled:
            pass  # todo

    # def transfer_single_local_to_minio(self, file_resource: SF):
    #     return file_resource.path().replace(self._local_dir, self._object_name_base)
