from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel


class ProgressSend:
    class AnalysisType(str, Enum):
        """分析类型枚举"""

        ANALYZE = "analyze"  # 智析
        COMPARE = "compare"  # 相似比较
        DIFF_COMPARE = "diffCompare"  # 差异比较
        INQUIRE = "inquire"  # 智查
        WRITE = "write"  # 智写

    class Dto(BaseModel):
        progress: Union[str, int] = "100"  # 当前步骤的进度, 百分数%
        step: str
        ratio: Union[str, int]  # 该步骤占整体进度的比值，百分数%
        type: Optional["ProgressSend.AnalysisType"] = None
        projectId: Union[str, int] = ""
        recordId: Union[str, int] = ""

    class Vo(BaseModel):
        """API响应视图对象"""

        code: str = ""
        reason: str = ""
        message: str = ""
        referenceError: str = ""
