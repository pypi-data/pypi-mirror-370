from typing import Optional

from pydantic import BaseModel


class DealAfterCaptableDetail(BaseModel):
    """
    shareholderID 投资主体ID
    dealId	项目ID                     \n
    dealName	项目名称                 \n
    changeDate	融资日期                 \n
    rounds	融资轮次                     \n
    shareholderName	股东名称             \n
    changeType	变更类型                 \n
    investAmount	本轮投资金额           \n
    resultShare	变更股数                 \n
    holdShare	最新持有股数               \n
    shareMarket	融资后持股市值              \n
    roundIncome	本轮盈利                 \n
    shareRatio	最新持股比例               \n
    remark	备注                       \n
    """
    shareholderId:Optional[str] = None
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    changeDate: Optional[str] = None
    rounds: Optional[str] = None
    shareholderName: Optional[str] = None
    changeType: Optional[str] = None
    investAmount: Optional[float] = None
    resultShare: Optional[float] = None
    holdShare: Optional[float] = None
    shareMarket: Optional[float] = None
    roundIncome: Optional[float] = None
    shareRatio: Optional[float] = None
    remark: Optional[str] = None
    companyId: Optional[str] = None
    companyName: Optional[str] = None
    changeId:Optional[str]=None
