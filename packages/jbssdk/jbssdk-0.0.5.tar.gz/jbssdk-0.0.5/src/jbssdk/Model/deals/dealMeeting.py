from typing import Optional

from pydantic import BaseModel


class DealBeforeMeeting(BaseModel):
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    meetingType: Optional[str] = None
    fundName: Optional[str] = None
    investAmount: Optional[float] = None
    investCurrency: Optional[str] = None
    actTitle: Optional[str] = None
    applyContent: Optional[str] = None
    mtDate: Optional[str] = None
    mtTime: Optional[str] = None
    mtConclusion: Optional[str] = None
    mtComment: Optional[str] = None
