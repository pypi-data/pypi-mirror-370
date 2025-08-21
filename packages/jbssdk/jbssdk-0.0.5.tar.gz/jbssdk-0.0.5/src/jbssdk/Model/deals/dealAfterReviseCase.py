from typing import Optional

from pydantic import BaseModel, Field


class DealAfterCathayCaseRevised(BaseModel):
    cathayCaseId: Optional[str] = None
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    investmentId: Optional[str] = None
    investorName: Optional[str] = None
    investorId:Optional[str] = None
    initialCaseAssumptions: Optional[str] = None
    reportDate: Optional[str] = None
    Revisedmaincaseassumptions: Optional[str] = Field(None, alias='Revised main case assumptions')
    Revisedupsidecaseassumptions: Optional[str] = Field(None, alias='Revised upside case assumptions')
    Reviseddownsidecaseassumptions: Optional[str] = Field(None, alias='Revised downside case assumptions')
    createTime: Optional[str] = None
    updateTime: Optional[str] = None
