from typing import Optional

from pydantic import BaseModel


class DealAfterValuation(BaseModel):
    """
    dealId	项目ID                                    \n
dealName	项目名称                                    \n
valuationId	项目估值ID                                  \n
company	是否上市                                        \n
valuationTime	估值时间                                \n
valuationMethod	估值方法                                \n
companyValuation	公司整体估值                          \n
totalNumberOfShares	总股数/注册资本                        \n
shareholdingRatio	持股比例                            \n
projectValuation	项目估值                            \n
currency	币种                                      \n
totalInvestmentCost	总投资成本                           \n
totalInvestmentRemainingCost	剩余投资成本              \n
valuationBackground	估值背景                            \n
    """
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    valuationId: Optional[str] = None
    company: Optional[str] = None  # 是,否
    valuationTime: Optional[str] = None
    valuationMethod: Optional[str] = None
    companyValuation: Optional[float] = None
    totalNumberOfShares: Optional[float] = None
    shareholdingRatio: Optional[float] = None
    projectValuation: Optional[float] = None
    currency: Optional[str] = None
    totalInvestmentCost: Optional[float] = None
    totalInvestmentRemainingCost: Optional[float] = None
    valuationBackground: Optional[str] = None
