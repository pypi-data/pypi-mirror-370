from typing import Optional, Union

from pydantic import BaseModel


class dealAfterPCW(BaseModel):
    """
    dealId	项目ID \n
    dealName	项目名称 \n
    pcwTableType	财务数据类型  \n
    dataSource	数据来源          \n
    reportingPeriod	报告周期   \n
    year	报告年份    \n
    keyName	财务指标   \n
    """
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    pcwTableType: Optional[str] = None
    dataSource: Optional[str] = None
    reportingPeriod: Optional[int] = None
    year: Optional[int] = None
    keyName: Optional[str] = None
    keyValue: Optional[Union[str, float]] = None
    companyId: Optional[str] = None
    companyName: Optional[str] = None
    currency: Optional[str] = None
