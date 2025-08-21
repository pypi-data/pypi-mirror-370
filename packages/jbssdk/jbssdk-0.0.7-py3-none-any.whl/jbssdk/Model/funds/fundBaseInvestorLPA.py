from typing import Optional

from pydantic import BaseModel


class FundBaseInvestorLPA(BaseModel):
    """
    fundId	基金ID                      \n
fundName	基金名称                      \n
investorId	出资人ID                     \n
investorName	出资人名称                 \n
clauseType	条款类型                      \n
clauseContent	条款内容                  \n
    """
    fundId: Optional[str] = None
    fundName: Optional[str] = None
    investorId: Optional[str] = None
    investorName: Optional[str] = None
    clauseType: Optional[str] = None
    clauseContent: Optional[str] = None
