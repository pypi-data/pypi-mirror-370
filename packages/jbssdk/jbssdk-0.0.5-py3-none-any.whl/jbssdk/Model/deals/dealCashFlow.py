from typing import Optional

from pydantic import BaseModel


class dealAfterCashFlow(BaseModel):
    """
    dealId	项目ID                    \n
dealName	项目名称                    \n
investmentName	承担主体                \n
type	现金流类型                       \n
operateType	业务类型                    \n
equityChangeTime	权益变更时间          \n
operateDate	发生时间                    \n
operateAmount	发生金额                \n
currency	币种                      \n
direction	方向                      \n
incomeType	流入类型                    \n
remark	备注                          \n
    """
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    investmentName: Optional[str] = None
    type: Optional[str] = None
    operateType: Optional[str] = None
    equityChangeTime: Optional[str] = None
    operateDate: Optional[str] = None
    operateAmount: Optional[float] = None
    currency: Optional[str] = None
    direction: Optional[str] = None
    incomeType: Optional[str] = None
    remark: Optional[str] = None
