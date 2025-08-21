from typing import Optional

from pydantic import BaseModel


class dealInfo(BaseModel):
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    companyName: Optional[str] = None
    stageName: Optional[str] = None
    website: Optional[str] = None
    addressDetail: Optional[str] = None
    businessDesc: Optional[str] = None
    companyDesc: Optional[str] = None
    industry: Optional[str] = None
    dealSource: Optional[str] = None
    reference: Optional[str] = None
    personChargeName: Optional[str] = None
    teamUserNames: Optional[str] = None
    financingRound: Optional[str] = None
    financingAmount: Optional[float] = None
    beforeValuationAmount: Optional[float] = None
    afterValuationAmount: Optional[float] = None
    financingCurrency: Optional[str] = None
    industrySegmentation: Optional[str] = None
    partenerLabel: Optional[str] = None
    investmentName: Optional[str] = None
    amountInvestmentEstimate: Optional[float] = None
    currency: Optional[str] = None
    provinceName: Optional[str] = None
    cityName: Optional[str] = None
    districtName: Optional[str] = None
    exitStatus: Optional[str] = None
    fiscal_year_month: Optional[str] = None
