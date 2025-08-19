import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import Generic, List, Type, TypeVar, Dict, Optional, Callable

import aiohttp
from loguru import logger

from huibiao_framework.client.data_model.ffcs import ProgressSend
from huibiao_framework.client import FfcsClient
from huibiao_framework.execption.ffcs import FfcsSendProgressError
from huibiao_framework.result import TaskResult
from huibiao_framework.task.resource_sync_minio import TaskResourceSyncMinio
from huibiao_framework.utils.annotation import frozen_attrs

TS = TypeVar("TS", bound=TaskResult)


def inner_step_annotation(step_name: str = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(self: "HuibiaoTask[TS]"):
            start_time = time.perf_counter()
            try:
                await func(self)
            except Exception as e:
                logger.error(f"{self.step_log_str(step_name)}失败, {str(e)}")
                raise e
            finally:
                elapsed = time.perf_counter() - start_time
                logger.info(f"{self.step_log_str(step_name)}耗时: {elapsed:.6f} 秒")
                self.time_cost_record[step_name] = elapsed

        return wrapper

    return decorator


@frozen_attrs(
    "task_type", "request_id", "project_id", "progress_send_analyse_type", "record_id"
)
class HuibiaoTask(Generic[TS], ABC):
    def __init__(
        self,
        *,
        task_type: Optional[str] = None,
        project_id: Optional[str] = None,
        request_id: Optional[str] = None,
        record_id: Optional[str] = None,
        task_result_cls: Type[TS],
        is_send_progress: bool = False,  # 是否发送进度
        progress_send_analyse_type: Optional[ProgressSend.AnalysisType],
    ):
        self.project_id = project_id
        self.task_type = task_type
        self.request_id = request_id
        self.record_id = record_id

        # 进度发送
        self.is_send_progress = is_send_progress
        self.progress_send_analyse_type = (
            progress_send_analyse_type  # 发送进度时需要指定一个任务类型
        )

        # 资源
        self.__result: TS = task_result_cls(task_type, project_id)
        self.__result_sync_client = TaskResourceSyncMinio(
            task_result=self.task_result
        )

        # 耗时
        self.time_cost_record: Dict[str, float] = {}
        self.__time_cost_all: float = 0

    @property
    def reqid(self):
        return self.request_id # 兼容旧的名称

    @property
    def task_result(self) -> TS:
        return self.__result

    @property
    def task_desc(self):
        return (
            f"[{self.task_type}][projId={self.project_id}][reqId={self.request_id}][recId={self.record_id}]"
        )

    def genSyncMinioClient(self) -> TaskResourceSyncMinio:
        return TaskResourceSyncMinio(task_result=self.task_result)

    @inner_step_annotation("pipeline前置初始化")
    async def init_task(self):
        await self.__result_sync_client.init()
        # 其他前置操作，加载任务上下文，待实现

    @inner_step_annotation("pipeline后置操作")
    async def post_action(self):
        """
        任务完成后的一些后处理步骤，后续丢到线程池里面执行
        """
        # 打印耗时
        step_time_cost_info = "\n".join(
            [f"|{k:40}|{v:10.5f}秒|" for k, v in self.time_cost_record.items()]
        )
        logger.info(f"\n{self.task_desc}整体耗时{self.__time_cost_all}，分步耗时：\n{step_time_cost_info}")
        await self.__result_sync_client.close()

    async def upload_result(self, resource_name: str):
        """
        将中间结果上传到minio
        """
        _resource_obj = self.task_result[resource_name]
        await self.__result_sync_client.upload_file(resource_name, _resource_obj)

    async def run_pipeline(self):
        await self.init_task()
        logger.info(f"{self.task_desc}任务初始化成功,开始执行任务")
        start = time.perf_counter()
        try:
            result = await self.pipeline()
            logger.info(f"{self.task_desc}任务完成")
            return result
        except Exception as e:
            logger.error(f"{self.task_desc}任务失败，报错{str(e)}")
            raise e
        finally:
            self.__time_cost_all = time.perf_counter() - start
            await self.post_action()

    @abstractmethod
    async def pipeline(self):
        """
        算法同事实现该部分
        """
        pass

    def step_log_str(self, step_name):
        return f"{self.task_desc}的[{step_name}]步骤"

    async def send_progress(
        self, progress_step_name: str, progress_step_ratio: str, progress: str
    ):
        # 传入空字符则不发送进度
        if self.is_send_progress and progress and progress_step_ratio and progress_step_name:
            progress_dto = ProgressSend.Dto(
                step=progress_step_name,
                ratio=progress_step_ratio,
                progress=progress,
                projectId=self.project_id,
                recordId=self.record_id,
                type=self.progress_send_analyse_type,
            )
            try:
                async with aiohttp.ClientSession() as _session:
                    client = FfcsClient(_session)
                    return await client.send_progress(progress_dto, reqid=self.request_id)
            except FfcsSendProgressError:
                pass

    @staticmethod
    def Step(step_name: str = None) -> 'StepAnnotationBuilder':
        return StepAnnotationBuilder(step_name)


class StepAnnotationBuilder:
    def __init__(self, step_name: str = None):
        self.__step_name = step_name
        # 步骤依赖的资源
        self.__depend: List[str] = []
        # 步骤产出的资源
        self.__output: Optional[str] = None
        # 步骤发生异常时是否忽略
        self.__ignore_error: bool = False
        # 进度 todo 进度步骤名建议和任务步骤名一致，需要算法同事配合
        self.__progress_step_name: Optional[str] = None
        self.__progress_step_ratio: Optional[str] = None
        self.__progress_start: Optional[str] = None
        self.__progress_end: Optional[str] = None

    def depends_on(self, *dependencies: str) -> "StepAnnotationBuilder":
        self.__depend.extend(dependencies)
        return self

    def produces(self, output: str) -> "StepAnnotationBuilder":
        self.__output = output
        return self

    def progress(self, step_ratio: str, step_name: str = None, start: str = "0", end: str = "100") -> "StepAnnotationBuilder":
        # 如果不指定进度的步骤名则默认用任务步骤名
        self.__progress_step_name = step_name if step_name is not None else self.__step_name
        self.__progress_step_ratio = step_ratio
        self.__progress_start = start
        self.__progress_end = end
        return self

    def ignore_error(self) -> "StepAnnotationBuilder":
        self.__ignore_error = True
        return self

    def raise_error(self):
        self.__ignore_error = False
        return self

    async def __send_progress(self, task_self: "HuibiaoTask[TS]", progress: str):
        # 进度推送，考虑后续改用多线程
        if self.__progress_step_name and self.__progress_step_ratio and progress:
            await task_self.send_progress(
                progress_step_name=self.__progress_step_name,
                progress_step_ratio=self.__progress_step_ratio,
                progress=progress,
            )

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(task_self: "HuibiaoTask[TS]", *args, **kwargs):

            name = builder.__step_name or func.__name__
            do_task = False
            elapsed: float = 0

            # 依赖资源检查（用builder访问配置，用task_self访问任务实例）
            if builder.__output is not None:
                if not task_self.task_result[builder.__output].is_completed():
                    do_task = True
                else:
                    logger.info(
                        f"{task_self.step_log_str(name)}产出资源[{builder.__output}]已完成"
                    )
            else:
                do_task = True

            if do_task:
                # 加载依赖资源
                for d_r in builder.__depend:
                    task_self.task_result[d_r].load()

                await builder.__send_progress(task_self, builder.__progress_start) # 进度推送
                logger.info(f"{task_self.step_log_str(name)}开始")
                start = time.perf_counter()
                try:
                    await func(task_self, *args, **kwargs)  # 调用原函数时传入任务实例
                    logger.info(f"{task_self.step_log_str(name)}成功")
                except Exception as e:
                    logger.error(f"{task_self.step_log_str(name)}失败: {str(e)}")
                    if not builder.__ignore_error:  # 检查builder的ignore_error配置
                        raise e
                finally:
                    elapsed = time.perf_counter() - start
                    logger.info(
                        f"{task_self.step_log_str(name)}，耗时: {elapsed:.6f} 秒"
                    )
                    task_self.time_cost_record[name] = elapsed  # 记录到任务实例的耗时

                await  builder.__send_progress(task_self, builder.__progress_end) # 进度推送

                if builder.__output is not None:
                    task_self.task_result[builder.__output].complete()
                    await task_self.upload_result(builder.__output)
            else:
                logger.info(f"{task_self.step_log_str(name)}已完成，跳过该步骤")
                task_self.time_cost_record[name] = elapsed

        # 将当前builder实例绑定到wrapper的闭包中，避免命名冲突
        builder = self
        return wrapper