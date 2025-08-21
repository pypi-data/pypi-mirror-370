from typing import Optional

from pydantic import BaseModel


class LPBaseInvestor(BaseModel):
    """
    lpId	投资人ID                         \n
lpName	投资人名称                             \n
fundId	基金ID                              \n
fundName	基金简称                          \n
fundStatus	基金阶段                          \n
subscribedAmount	基金总规模                 \n
accumulatedPaidMount	基金实缴金额            \n
valuationTime	基金估值                      \n
currency	币种                            \n
timeSubscription	认缴时间                  \n
lpSubscribedAmount	认缴金额                  \n
lpSubscriptionRate	认缴比例                  \n
lpAccumulatedPaidMount	实缴金额              \n
paidInProgress	缴款比例                      \n
NAV	NAV                                   \n
allocationAmount	分配总额                  \n
    """
    lpId: Optional[str] = None
    lpName: Optional[str] = None
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    fundStatus: Optional[str] = None
    subscribedAmount: Optional[float] = None
    accumulatedPaidMount: Optional[float] = None
    valuationTime: Optional[str] = None
    currency: Optional[str] = None
    timeSubscription: Optional[str] = None
    lpSubscribedAmount: Optional[float] = None
    lpSubscriptionRate: Optional[float] = None
    lpAccumulatedPaidMount: Optional[float] = None
    paidInProgress: Optional[float] = None
    NAV: Optional[float] = None
    allocationAmount: Optional[float] = None
