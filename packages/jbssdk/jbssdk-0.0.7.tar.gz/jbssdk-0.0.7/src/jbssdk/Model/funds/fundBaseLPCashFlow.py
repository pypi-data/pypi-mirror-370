from typing import Optional

from pydantic import BaseModel


class FundBaseLPCashFlow(BaseModel):
    """
    fundId	基金ID                     \n
fundName	基金名称                     \n
lpName	出资人名称                        \n
lpId	出资人ID                        \n
type	现金流类型                        \n
businessType	业务类型                 \n
direction	方向                       \n
operateDate	发生时间                     \n
operateAmount	发生金额                 \n
currency	币种                       \n
remark	备注                           \n
    """
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    lpName: Optional[str] = None
    lpId: Optional[str] = None
    type: Optional[str] = None
    businessType: Optional[str] = None
    direction: Optional[str] = None
    operateDate: Optional[str] = None
    operateAmount: Optional[float] = None
    currency: Optional[str] = None
    remark: Optional[str] = None
