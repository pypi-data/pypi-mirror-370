from typing import Optional

from pydantic import BaseModel


class FundBaseCashFlow(BaseModel):
    """
    fundId	基金ID                     \n
fundName	基金名称                     \n
type	现金流类型                        \n
operateType	业务类型                     \n
equityChangeTime	权益变更时间           \n
operateDate	发生时间                     \n
currency	币种                       \n
operateAmount	发生金额                 \n
direction	方向                       \n
incomeType	流入类型                     \n
remark	备注                           \n
dealId	项目ID                         \n
dealName	项目名称                     \n
    """
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    type: Optional[str] = None
    operateType: Optional[str] = None
    equityChangeTime: Optional[str] = None
    operateDate: Optional[str] = None
    currency: Optional[str] = None
    operateAmount: Optional[float] = None
    direction: Optional[str] = None
    incomeType: Optional[str] = None
    remark: Optional[str] = None
    dealId: Optional[str] = None
    dealName: Optional[str] = None
