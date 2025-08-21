from typing import Optional

from pydantic import BaseModel


class FundBaseIncome(BaseModel):
    """
    fundId	基金ID                                          \n
fundName	基金名称                                          \n
distributionDate	回款时间                                  \n
equityChangeTime	权益变更时间                                \n
typeFee	收益类型                                              \n
amountIncome	收益                                        \n
currency	币种                                            \n
distributionLp	收益是否已经分配给出资人                              \n
shareWay	分摊方式                                          \n
remark	备注                                                \n
dealName	回款项目                                          \n
amountPrincipal	本金                                        \n
amountBonus	分红                                            \n
amountOthers	其他                                        \n
amountDistribution	回款总额                                  \n
    """
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    distributionDate: Optional[str] = None
    equityChangeTime: Optional[str] = None
    typeFee: Optional[str] = None
    amountIncome: Optional[float] = None
    currency: Optional[str] = None
    distributionLp: Optional[str] = None
    shareWay: Optional[str] = None
    remark: Optional[str] = None
    dealName: Optional[str] = None
    amountPrincipal: Optional[float] = None
    amountBonus: Optional[float] = None
    amountOthers: Optional[float] = None
    amountDistribution: Optional[float] = None
