from typing import Optional

from pydantic import BaseModel


class FundBaseInfoPhase(BaseModel):
    """
    fundId	基金ID                 \n
fundName	基金简称                 \n
fundFullName	基金全称             \n
phase	阶段                       \n
term	期限                       \n
startDate	起始日期                 \n
endDate	结束日期                     \n
accrualBase	计提基数                 \n
    """
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    fundFullName: Optional[str] = None
    phase: Optional[str] = None
    term: Optional[float] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    accrualBase: Optional[str] = None
