from typing import Optional

from pydantic import BaseModel


class DealUser(BaseModel):
    nickName: Optional[str] = None


class DealDept(BaseModel):
    deptName: Optional[str] = None


class DealAfterExitStrategy(BaseModel):
    """
    dealId	项目ID
dealName	项目名称
actTitle	申请标题
exitStrategy	退出策略
totalInvestment	总投资额
dealUser.nickName	项目负责人
dealDept.deptName	所属部门
investmentTime	投资时间
latestShareholdingRatio	最新持股比例
reinvestmentCost	在投成本
exitTotal	已退出总额
draftExitTime	拟退出时间
draftExitPrice	拟退出金额
draftExitShareholdingRatio	拟退出持股比例
draftExitShareholdingCapital	拟退出持股股本
priorWay	优先退出方式
spareWay	备选退出方式
lowestWay	保底退出方式
exitSharesNumber	退出股数
expectPerSharePrice	预计每股均价
transferee	受让方
multiple	倍数
irr	IRR
reportTime	报告时间
remark	备注
potentialExitOptions	其他潜在退出方案
investmentTaxStructure	投资税务架构
feasibilityRisks	可行性及潜在风险
mainHolderRatioKgq	主要股东及比例
expectSellKgq	预计出售估值
dragAlongRightsKgq	是否有拖售权
potentialBuyerKgq	潜在买家范围
nextPlanKgq	下一步计划
sellRatioSsgq	拟出售比例
sellOpportunitySsgq	出售时机
expectSellSsgq	预计出售估值
potentialBuyerSsgq	潜在买家范围
nextPlanSsgq	下一步计划
triggerRepurchaseHg	何时触发回购
expectRecoverMoneyHg	预计回收金额
nextPlanHg	下一步计划
expectListedAddressIpo	预计上市地
listedTimeIpo	申报/上市时间
listedLockPeriodIpo	上市后锁定期
focusItemIpo	需关注事项
nextPlanIpo	下一步计划
reasonHoldingGc	继续持有原因
focusItemGc	关注事项
actionAndFocus	下一步计划
    """
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    actTitle: Optional[str] = None
    exitStrategy: Optional[str] = None
    totalInvestment: Optional[float] = None
    dealUser: Optional[DealUser] = None
    dealDept: Optional[DealDept] = None
    investmentTime: Optional[str] = None
    latestShareholdingRatio: Optional[float] = None
    reinvestmentCost: Optional[float] = None
    exitTotal: Optional[float] = None
    draftExitTime: Optional[str] = None
    draftExitPrice: Optional[float] = None
    draftExitShareholdingRatio: Optional[float] = None
    draftExitShareholdingCapital: Optional[str] = None
    priorWay: Optional[str] = None
    spareWay: Optional[str] = None
    lowestWay: Optional[str] = None
    exitSharesNumber: Optional[float] = None
    expectPerSharePrice: Optional[str] = None
    transferee: Optional[str] = None
    multiple: Optional[str] = None
    irr: Optional[str] = None
    reportTime: Optional[str] = None
    remark: Optional[str] = None
    potentialExitOptions: Optional[str] = None
    investmentTaxStructure: Optional[str] = None
    feasibilityRisks: Optional[str] = None
    mainHolderRatioKgq: Optional[str] = None
    expectSellKgq: Optional[str] = None
    dragAlongRightsKgq: Optional[str] = None
    potentialBuyerKgq: Optional[str] = None
    nextPlanKgq: Optional[str] = None
    sellRatioSsgq: Optional[str] = None
    sellOpportunitySsgq: Optional[str] = None
    expectSellSsgq: Optional[str] = None
    potentialBuyerSsgq: Optional[str] = None
    nextPlanSsgq: Optional[str] = None
    triggerRepurchaseHg: Optional[str] = None
    expectRecoverMoneyHg: Optional[float] = None
    nextPlanHg: Optional[str] = None
    expectListedAddressIpo: Optional[str] = None
    listedTimeIpo: Optional[str] = None
    listedLockPeriodIpo: Optional[str] = None
    focusItemIpo: Optional[str] = None
    nextPlanIpo: Optional[str] = None
    reasonHoldingGc: Optional[str] = None
    focusItemGc: Optional[str] = None
    actionAndFocus: Optional[str] = None
