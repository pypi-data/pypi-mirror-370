from typing import Optional

from pydantic import BaseModel


class FundBaseExpense(BaseModel):
    """
    fundId	基金ID                         \n
fundName	基金名称                         \n
typesFee	费用类型                         \n
applyTime	发生时间                         \n
amountMoney	费用金额                         \n
type	类型                               \n
costAttribution	费用归属                     \n
shareItem	分摊项目                         \n
payCompletionTime	付款完成时间               \n
costsThat	费用明细                         \n
whetherAddedTax	      是否考虑增值税                 \n
addedTax	税率                    \n
actualPaymentAmount	基金实际支付金额               \n
    """
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    typesFee: Optional[str] = None
    applyTime: Optional[str] = None
    amountMoney: Optional[float] = None
    type: Optional[str] = None
    costAttribution: Optional[str] = None
    shareItem: Optional[str] = None
    payCompletionTime: Optional[str] = None
    costsThat: Optional[str] = None
    whetherAddedTax: Optional[str] = None
    addedTax: Optional[float] = None
    actualPaymentAmount: Optional[float] = None
