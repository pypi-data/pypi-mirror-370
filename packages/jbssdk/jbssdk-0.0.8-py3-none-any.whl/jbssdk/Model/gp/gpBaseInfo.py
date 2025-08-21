from typing import Optional

from pydantic import BaseModel


class GPBaseInfo(BaseModel):
    """
    管理公司ID	gpId                            \n
管理人全称	gpName                              \n
管理人简称	gpShortName                         \n
成立时间	setDate                             \n
企业统一社会信用代码	creditCode                      \n
法定代表人	legalPerson                         \n
注册地	detailsRegistered                       \n
    """
    gpId: Optional[str] = None
    gpName: Optional[str] = None
    gpShortName: Optional[str] = None
    setDate: Optional[str] = None
    creditCode: Optional[str] = None
    legalPerson: Optional[str] = None
    detailsRegistered: Optional[str] = None
