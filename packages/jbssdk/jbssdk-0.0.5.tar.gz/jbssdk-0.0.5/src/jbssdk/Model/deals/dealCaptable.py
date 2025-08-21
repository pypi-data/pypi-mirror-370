from typing import Optional

from pydantic import BaseModel


class dealAfterCaptable(BaseModel):
    """
    dealId	项目ID \n
    dealName	项目名称 \n
    changeDate	融资日期 \n
    rounds	融资轮次 \n
    amountFinancing	融资总金额 \n
    currency	币种 \n
    beforeValuation	融资前公司估值 \n
    afterValuation	融资后公司估值\n
    roundsType	融资方式\n
    beforeShareNum	融资前注册资本\n
    afterShareNum	融资后注册资本\n
    afterSharePrice	融资后每股价格\n
    """
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    changeDate: Optional[str] = None
    rounds: Optional[str] = None
    amountFinancing: Optional[float] = None
    currency: Optional[str] = None
    beforeValuation: Optional[float] = None
    afterValuation: Optional[float] = None
    roundsType: Optional[str] = None
    beforeShareNum: Optional[float] = None
    afterShareNum: Optional[float] = None
    afterSharePrice: Optional[float] = None
    companyId: Optional[str] = None
    companyName: Optional[str] = None
