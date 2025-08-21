from typing import Optional

from pydantic import BaseModel, Field


class DealAfterInvestmentCaseDetail(BaseModel):
    """
    Model for deal details after investment, based on the provided table structure.
    """
    cathay_case_id: Optional[str] = Field(None, alias='cathayCaseId', description="数据 ID")
    date: Optional[str] = Field(None, alias='Date', description="Date")
    type: Optional[str] = None
    cathay_net_equity_value_m: Optional[str] = Field(None, alias='Cathay Net Equity Value(M)',
                                                     description="Cathay Net Equity Value(M)")
    partial_exit_m: Optional[str] = Field(None, alias='Partial Exit(M)', description="Partial Exit(M)")
    dividends_distributed_m: Optional[str] = Field(None, alias='Dividends distributed(M)',
                                                   description="Dividends distributed(M)")
    percentage_of_the_company: Optional[str] = Field(None, alias='% of the company', description="% of the company")
    cathay_irr: Optional[str] = Field(None, alias='Cathay IRR', description="Cathay IRR")
    cathay_mm: Optional[str] = Field(None, alias='Cathay MM', description="Cathay MM")
    sales_m: Optional[str] = Field(None, alias='Sales(M)', description="Sales(M)")
    gross_margin: Optional[str] = Field(None, alias='Gross margin', description="Gross margin")
    p_e: Optional[str] = Field(None, alias='P / E', description="P / E")
    ebitda_m: Optional[str] = Field(None, alias='EBITDA(M)', description="EBITDA(M)")
    ev_ebitda: Optional[str] = Field(None, alias='EV / EBITDA', description="EV / EBITDA")
    enterprise_value_m: Optional[str] = Field(None, alias='Enterprise Value(M)', description="Enterprise Value(M)")
    further_dilution_if_any: Optional[str] = Field(None, alias='Further dilution (if any)',
                                                   description="Further dilution (if any)")
    equity_value_post_money_m: Optional[str] = Field(None, alias='Equity value (post money)(M)',
                                                     description="Equity value (post money)(M)")
