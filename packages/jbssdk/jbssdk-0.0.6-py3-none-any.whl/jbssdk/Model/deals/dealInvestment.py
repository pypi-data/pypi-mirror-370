from typing import Optional
from pydantic import BaseModel

class DealAfterInvestment(BaseModel):
    """
    dealId: 项目ID\n
    dealName: 项目名称\n
    investmentName: 投资主体\n
    currency: 投资币种\n
    dateInvestmentEstimate: 预计投资时间\n
    investmentSignTime: 投资协议签署时间\n
    dateInvestmentFact: 首次付款时间\n
    amountInvestmentEstimate: 预计投资金额\n
    agreementMoney: 协议金额\n
    amountInvestmentFact: 实际投资金额\n
    initialShareholdingRatio: 进入时持股比例\n
    latestShareholdingRatio: 最新持股比例\n
    numberOfShares: 最新持股数量\n
    totalAmountReceived: 已回款总金额\n
    paidPrincipal: 已回款本金\n
    receivedIncome: 已回款收益\n
    IRR: IRR\n
    latestValuationDate: 最新估值时间\n
    holdingPartialValuation: 持有部分估值\n
    investmentRole: 投资角色
    """
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    investmentId:Optional[str] = None
    investmentName: Optional[str] = None
    currency: Optional[str] = None
    dateInvestmentEstimate: Optional[str] = None
    investmentSignTime: Optional[str] = None
    dateInvestmentFact: Optional[str] = None
    amountInvestmentEstimate: Optional[float] = None
    agreementMoney: Optional[float] = None
    amountInvestmentFact: Optional[float] = None
    initialShareholdingRatio: Optional[float] = None
    latestShareholdingRatio: Optional[float] = None
    numberOfShares: Optional[float] = None
    totalAmountReceived: Optional[float] = None
    paidPrincipal: Optional[float] = None
    receivedIncome: Optional[float] = None
    IRR: Optional[float] = None
    latestValuationDate: Optional[str] = None
    holdingPartialValuation: Optional[float] = None
    investmentRole: Optional[str] = None