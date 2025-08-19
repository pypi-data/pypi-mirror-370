import time
from typing import Union, Optional, final
from loguru import logger

import aiohttp

from huibiao_framework.client import FfcsClient
from huibiao_framework.client.data_model.ffcs import ProgressSend


class FfcStepProgressBar:
    """
    福富进度条
    """

    def __init__(
        self,
        *,
        step: str,
        requestId: str,
        ratio: Union[str, int],
        projectId: Union[str, int],
        recordId: Union[str, int],
        send_threshold_sec: int = 2,
        type: Optional[ProgressSend.AnalysisType],
    ):
        self.requestId = requestId
        self.ratio = str(ratio)
        self.projectId = str(projectId)
        self.recordId = str(recordId)
        self.step = step
        self.type = type

        # 初始化进度追踪
        self.__last_progress = 0
        self.__last_send_time = None  # 添加上次发送进度的时间戳
        self.__send_threshold_sec = send_threshold_sec # 进度发送间隔，不能太频繁
        self.__complete = False  # 是否成功100的进度

    def __str__(self):
        return f"FfcStepProgressBar[{self.step}][{self.requestId}][{self.projectId}]"

    def __is_time_interval_enable(self, current_time) -> bool:
        if self.__last_send_time is None:
            return True

        assert current_time is not None

        interval: int = current_time - self.__last_send_time
        if interval <= self.__send_threshold_sec:
            logger.warning(f"{self}进度发送冷却中，距上次{interval}秒")
            return False

        return True

    async def __send_progress(self, progress: Union[str, int]):
        if self.__complete:
            logger.warning(f"{self}已完成，请勿重复发送")
            return

        current_time = time.time()
        if progress == 100 or self.__is_time_interval_enable(current_time=current_time):
            async with aiohttp.ClientSession() as session:
                client = FfcsClient(session)
                try:
                    await client.send_progress(
                        ProgressSend.Dto(
                            step=self.step,
                            ratio=self.ratio,
                            progress=str(progress),
                            projectId=self.projectId,
                            recordId=self.recordId,
                            type=self.type,
                        ),
                        self.requestId,
                    )
                    self.__last_send_time = current_time
                    if progress == 100:
                        self.__complete = True
                        logger.info(f"{self}完成！")
                finally:
                    pass

    def set_progress(self, progress: Union[str, int]) -> "FfcStepProgressBar":
        p = int(progress)
        assert 0 < p <= 100, f"{self}进度必须大于0小于等于100"
        assert p >= self.__last_progress, f"{self}进度只能递增，当前进度{self.__last_progress}，新进度{p}"
        old_p = self.__last_progress
        self.__last_progress = p
        logger.info(f"{self}进度更新 {old_p}%->{p}%")
        return self

    @final
    async def send_progress(self):
        await self.__send_progress(self.__last_progress)


class ItemCountFcStepProgressBar(FfcStepProgressBar):
    def __init__(self, item_num: int, **kwargs):
        self.__item_num = item_num # 总数量
        self.__complete_num = 0
        super().__init__(**kwargs)

    def cumulate(self) -> "FfcStepProgressBar":
        """
        完成数+1
        """
        assert self.__item_num > self.__complete_num
        self.__complete_num += 1
        new_progress = int(100 * self.__complete_num / self.__item_num)
        logger.info(f"{self} {self.__complete_num}/{self.__item_num}")
        super().set_progress(new_progress)
        return self

    @final
    def set_progress(self, progress: Union[str, int]) -> "FfcStepProgressBar":
        """
        不允许用户自己计算进度
        """
        logger.warning(f"{self}不允许用户自己修改进度")
        return self