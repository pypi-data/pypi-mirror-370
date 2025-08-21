from typing import Optional

from pydantic import BaseModel


class DealAfterTerms(BaseModel):
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    termsType: Optional[str] = None
    remark: Optional[str] = None
    summaryContent: Optional[str] = None
    sourceContract: Optional[str] = None
