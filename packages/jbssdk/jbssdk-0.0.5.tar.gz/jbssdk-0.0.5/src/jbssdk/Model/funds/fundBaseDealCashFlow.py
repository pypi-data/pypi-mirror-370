from typing import Optional

from pydantic import BaseModel


class FundBaseDealCashFlow(BaseModel):
    """
    fundId	基金ID
    fundNme	基金名称
    dealName	项目名称
    dealId	项目ID
    type	现金流类型
    operateType	业务类型
    equityChangeTime	权益变更时间
    operateDate	发生时间
    operateAmount	发生金额
    currency	币种
    direction	方向
    incomeType	流入类型
    remark	备注
    """
    fundId: Optional[str] = None
    fundNme: Optional[str] = None
    dealName: Optional[str] = None
    dealId: Optional[str] = None
    type: Optional[str] = None
    operateType: Optional[str] = None
    equityChangeTime: Optional[str] = None
    operateDate: Optional[str] = None
    operateAmount: Optional[float] = None
    currency: Optional[str] = None
    direction: Optional[str] = None
    incomeType: Optional[str] = None
    remark: Optional[str] = None
    operateAmountRmb: Optional[float] = None