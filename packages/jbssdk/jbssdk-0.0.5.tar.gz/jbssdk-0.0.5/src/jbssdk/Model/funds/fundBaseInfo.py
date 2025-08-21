from typing import Optional

from pydantic import BaseModel


class FundBaseInfo(BaseModel):
    """
    fundId	基金ID                               \n
    fundName	基金简称                           \n
    fundFullName	基金全称                       \n
    fundStatus	基金状态                           \n
    fundType	基金类型                           \n
    targetAmount	基金目标募集规模                   \n
    personCharge	基金负责人                      \n
    currency	币种                             \n
    foundationDate	基金成立日                      \n
    creditCode	企业统一社会信用代码                     \n
    sCode	基金编码                               \n
    provinceRegistered	注册省                    \n
    cityRegistered	注册市                        \n
    fundManager	基金管理人                          \n
    fundClosingDate	基金关账日                      \n
    investmentObjective	投资目标                   \n
    """
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    fundFullName: Optional[str] = None
    fundStatus: Optional[str] = None
    fundType: Optional[str] = None
    targetAmount: Optional[float] = None
    personCharge: Optional[str] = None
    currency: Optional[str] = None
    foundationDate: Optional[str] = None
    creditCode: Optional[str] = None
    sCode: Optional[str] = None
    provinceRegistered: Optional[str] = None
    cityRegistered: Optional[str] = None
    fundManager: Optional[str] = None
    fundClosingDate: Optional[str] = None
    investmentObjective: Optional[str] = None
