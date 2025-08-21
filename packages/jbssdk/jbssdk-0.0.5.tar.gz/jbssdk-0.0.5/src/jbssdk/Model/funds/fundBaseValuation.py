from typing import Optional

from pydantic import BaseModel


class FundBaseValuation(BaseModel):
    """
    fundId	基金ID                                            \n
fundName	基金名称                                            \n
investedItemNum	已投标的个数                                      \n
fundraisingScale	实际募资规模                                  \n
investScale	已投规模                                            \n
fundCost	基金费用                                            \n
surplusScale	剩余规模                                        \n
totalProjectRefund	投资回款总额                                  \n
fundDistributionAmount	基金分配金额                              \n
portfolioValuationAmount	投资组合估值                          \n
sumOfNonProjectIncome	非项收益                                \n
valuationTime	估值时间                                        \n
valuationAmount	估值金额                                        \n
    """
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    investedItemNum: Optional[float] = None
    fundraisingScale: Optional[float] = None
    investScale: Optional[float] = None
    fundCost: Optional[float] = None
    surplusScale: Optional[float] = None
    totalProjectRefund: Optional[float] = None
    fundDistributionAmount: Optional[float] = None
    portfolioValuationAmount: Optional[float] = None
    sumOfNonProjectIncome: Optional[float] = None
    valuationTime: Optional[str] = None
    valuationAmount: Optional[float] = None
