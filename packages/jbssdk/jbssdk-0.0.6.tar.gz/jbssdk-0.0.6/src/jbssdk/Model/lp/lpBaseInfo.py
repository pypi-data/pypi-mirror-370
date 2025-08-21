from typing import Optional

from pydantic import BaseModel


class LPBaseInfo(BaseModel):
    """
    lpId	投资人ID
lpName	客户全称
lpShortName	客户简称
manager	负责人
lpClassify	客户分类
lpType	客户类型
provinceRegistered	注册地-省
cityRegistered	注册地-市
capitalSource	资金来源
proportionRequirements	反投比例要求
    """
    lpId: Optional[str] = None
    lpName: Optional[str] = None
    lpShortName: Optional[str] = None
    manager: Optional[str] = None
    lpClassify: Optional[str] = None
    lpType: Optional[str] = None
    provinceRegistered: Optional[str] = None
    cityRegistered: Optional[str] = None
    capitalSource: Optional[str] = None
    proportionRequirements: Optional[str] = None
