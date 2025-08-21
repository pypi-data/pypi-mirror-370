from typing import Optional

from pydantic import BaseModel


class DealAfterCathayCaseInitial(BaseModel):
    """
    cathayCaseId	数据ID
    dealId	项目ID
    dealName	项目名称
    investmentId	投资主体ID
    investorName	投资主体名称
    initialCaseAssumptions	Initial Case Assumptions
    createTime	创建时间
    updateTime	修改时间
    """
    cathayCaseId: Optional[str] = None
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    investmentId: Optional[str] = None
    investorId:Optional[str] = None
    investorName: Optional[str] = None
    initialCaseAssumptions: Optional[str] = None
    createTime: Optional[str] = None
    updateTime: Optional[str] = None
