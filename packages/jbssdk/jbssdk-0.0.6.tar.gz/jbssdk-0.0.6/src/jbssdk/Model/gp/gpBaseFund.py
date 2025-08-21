from typing import Optional

from pydantic import BaseModel


class GPBaseFund(BaseModel):
    """
    管理公司ID	gpId          \n
管理人全称	gpName            \n
类型	type                  \n
基金ID	fundId            \n
基金名称	fundName          \n
    """
    gpId: Optional[str] = None
    gpName: Optional[str] = None
    type: Optional[str] = None
    fundId: Optional[str] = None
    fundName: Optional[str] = None
