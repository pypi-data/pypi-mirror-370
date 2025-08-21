from typing import Optional

from pydantic import BaseModel


class dealAfterValuationInvestment(BaseModel):
    """
    dealId	项目ID                            \n
dealName	项目名称                            \n
valuationId	项目估值ID                          \n
investmentName	主体名称                        \n
amountInvestmentFact	实际投资金额              \n
remainingInvestmentCost	剩余投资成本              \n
latestShareholdingRatio	最新持股比例%             \n
numberOfShares	主体持股数量                      \n
fundProjectValuation	主体所占项目估值            \n
    """
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    valuationId: Optional[str] = None
    investmentName: Optional[str] = None
    amountInvestmentFact: Optional[float] = None
    remainingInvestmentCost: Optional[float] = None
    latestShareholdingRatio: Optional[float] = None
    numberOfShares: Optional[float] = None
    fundProjectValuation: Optional[float] = None
