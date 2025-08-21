from typing import Optional

from pydantic import BaseModel


class FundBaseInvestor(BaseModel):
    """
    fundId	基金ID                                          \n
fundName	基金名称                                          \n
investorType	出资人类型                                     \n
investorName	出资人名称                                     \n
partnerType	合伙人类型                                         \n
investmentTime	合伙协议签订时间                                  \n
timeSubscription	认缴时间                                  \n
subscribedAmount	认缴金额                                  \n
subscriptionRate	认缴比例                                  \n
accumulatedPaidMount	累计实缴金额                            \n
latestIrr	最新IRR                                         \n
subInvestAmount	认缴出资余额                                    \n
allocationAmount	累计分配金额                                \n
taxeFee	税费                                                \n
managerFee	累计管理费                                         \n
otherFee	其他费用                                          \n
incomeFee	投资收益                                          \n
amountBalance	资本账户余额                                    \n
valuationAmount	所占基金估值                                    \n
paidInProgress	缴款进度                                      \n
DPI	DPI                                                   \n
TVPI	TVPI                                              \n
latestIrr	Net IRR                                       \n
RVPI	RVPI                                              \n
    """
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    investorType: Optional[str] = None
    investorName: Optional[str] = None
    partnerType: Optional[str] = None
    investmentTime: Optional[str] = None
    timeSubscription: Optional[str] = None
    subscribedAmount: Optional[float] = None
    subscriptionRate: Optional[float] = None
    accumulatedPaidMount: Optional[float] = None
    latestIrr: Optional[float] = None
    subInvestAmount: Optional[float] = None
    allocationAmount: Optional[float] = None
    taxeFee: Optional[float] = None
    managerFee: Optional[float] = None
    otherFee: Optional[float] = None
    incomeFee: Optional[float] = None
    amountBalance: Optional[float] = None
    valuationAmount: Optional[float] = None
    paidInProgress: Optional[float] = None
    DPI: Optional[float] = None
    TVPI: Optional[float] = None
    # latestIrr: Optional[str] = None
    RVPI: Optional[float] = None
