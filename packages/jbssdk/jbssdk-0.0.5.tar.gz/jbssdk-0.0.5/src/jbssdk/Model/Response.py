from typing import Optional, List, Any, TypeVar

from pydantic import BaseModel

from .deals.dealAfterExitStrategy import DealAfterExitStrategy
from .deals.dealAfterInitialCase import DealAfterCathayCaseInitial
from .deals.dealAfterInvestmentCaseDetail import DealAfterInvestmentCaseDetail
from .deals.dealAfterReviseCase import DealAfterCathayCaseRevised
from .deals.dealCaptable import dealAfterCaptable
from .deals.dealCaptableDetail import DealAfterCaptableDetail
from .deals.dealCashFlow import dealAfterCashFlow
from .deals.dealInfo import dealInfo
from .deals.dealInvestment import DealAfterInvestment
from .deals.dealInvestmentEvaluation import DealAfterInvestEvaluation
from .deals.dealMeeting import DealBeforeMeeting
from .deals.dealPCW import dealAfterPCW
from .deals.dealTerms import DealAfterTerms
from .deals.dealTrack import DealBeforeTrack
from .deals.dealValuation import DealAfterValuation
from .deals.dealValuationInvestment import dealAfterValuationInvestment
from .funds.fundBaseCashFlow import FundBaseCashFlow
from .funds.fundBaseDealCashFlow import FundBaseDealCashFlow
from .funds.fundBaseExpense import FundBaseExpense
from .funds.fundBaseIncome import FundBaseIncome
from .funds.fundBaseInfo import FundBaseInfo
from .funds.fundBaseInfoPhase import FundBaseInfoPhase
from .funds.fundBaseInvestor import FundBaseInvestor
from .funds.fundBaseInvestorLPA import FundBaseInvestorLPA
from .funds.fundBaseLPCashFlow import FundBaseLPCashFlow
from .funds.fundBaseValuation import FundBaseValuation
from .gp.gpBaseFund import GPBaseFund
from .gp.gpBaseInfo import GPBaseInfo
from .lp.lpBaseInfo import LPBaseInfo
from .lp.lpBaseInvestor import LPBaseInvestor
from .lp.lpBaseTrack import LPBaseTrack
from .system.hrbase import HRBase
from .system.rate import SysExchangeRate
from .system.rateDetail import SysExchangeRateDetail


class JBSResponse(BaseModel):
    code: int
    msg: str
    datas: dict[str, Any]


T = TypeVar("T", bound="JBSResponse")  # 定义一个类型变量，绑定到 JBSResponse 或其子类


class getDealBeforeInfoResponse(JBSResponse):
    data: Optional[List[dealInfo]] = None


class getDealBeforeTrackTrackResponse(JBSResponse):
    data: Optional[List[DealBeforeTrack]] = None


class getDealBeforeMeetingResponse(JBSResponse):
    data: Optional[List[DealBeforeMeeting]] = None


class getDealAfterInfoResponse(JBSResponse):
    data: Optional[List[dealInfo]] = None


class getDealAfterInvestmentResponse(JBSResponse):
    data: Optional[List[DealAfterInvestment]] = None


class getDealAfterTermsResponse(JBSResponse):
    data: Optional[List[DealAfterTerms]] = None


class getDealAfterPCWResponse(JBSResponse):
    data: Optional[List[dealAfterPCW]] = None


class getDealAfterCaptableResponse(JBSResponse):
    data: Optional[List[dealAfterCaptable]] = None


class getDealAfterCaptableDetailResponse(JBSResponse):
    data: Optional[List[DealAfterCaptableDetail]] = None


class getDealAfterInvestEvaluationResponse(JBSResponse):
    data: Optional[List[DealAfterInvestEvaluation]] = None


class getDealAfterCashFlowResponse(JBSResponse):
    data: Optional[List[dealAfterCashFlow]] = None


class getDealAfterValuationResponse(JBSResponse):
    data: Optional[List[DealAfterValuation]] = None


class getDealAfterValuationInvestmentResponse(JBSResponse):
    data: Optional[List[dealAfterValuationInvestment]] = None


class getFundBaseInfoResponse(JBSResponse):
    data: Optional[List[FundBaseInfo]] = None


class getFundBaseInfoPhaseResponse(JBSResponse):
    data: Optional[List[FundBaseInfoPhase]] = None


class getFundBaseInvestorResponse(JBSResponse):
    data: Optional[List[FundBaseInvestor]] = None


class getFundBaseInvestorLPAResponse(JBSResponse):
    data: Optional[List[FundBaseInvestorLPA]] = None


class getFundBaseCashFlowResponse(JBSResponse):
    data: Optional[List[FundBaseCashFlow]] = None


class getFundBaseLPCashFlowResponse(JBSResponse):
    data: Optional[List[FundBaseLPCashFlow]] = None


class getFundBaseValuationResponse(JBSResponse):
    data: Optional[List[FundBaseValuation]] = None


class getFundBaseExpenseResponse(JBSResponse):
    data: Optional[List[FundBaseExpense]] = None


class getFundBaseIncomeResponse(JBSResponse):
    data: Optional[List[FundBaseIncome]] = None


class getLPBaseInfoResponse(JBSResponse):
    data: Optional[List[LPBaseInfo]] = None


class getLPBaseTrackResponse(JBSResponse):
    data: Optional[List[LPBaseTrack]] = None


class getLPBaseInvestorResponse(JBSResponse):
    data: Optional[List[LPBaseInvestor]] = None


class getGPBaseInfoResponse(JBSResponse):
    data: Optional[List[GPBaseInfo]] = None


class getGPBaseFundResponse(JBSResponse):
    data: Optional[List[GPBaseFund]] = None


class innerAPIData(BaseModel):
    code: int
    datas: Any
    msg: int
    rows: List[dict[str, Any]]


class getFundBaseDealCashFlowResponse(JBSResponse):
    data: Optional[List[FundBaseDealCashFlow]] = None


class getDealAfterExitStrategyResponse(JBSResponse):
    data: Optional[List[DealAfterExitStrategy]] = None


class getDealAfterCathayCaseInitialResponse(JBSResponse):
    data: Optional[List[DealAfterCathayCaseInitial]] = None


class getDealAfterCathayCaseRevisedResponse(JBSResponse):
    data: Optional[List[DealAfterCathayCaseRevised]] = None


class getDealAfterInvestmentCaseDetailResponse(JBSResponse):
    data: Optional[List[DealAfterInvestmentCaseDetail]] = None


# 首页看板专用


class innerAPIDashBoardViewResponse(JBSResponse):
    data: innerAPIData


# 通用
class innerAPICommonResponse(JBSResponse):
    data: Any


class getSysExchangeRateResponse(JBSResponse):
    data: Optional[List[SysExchangeRate]] = None


class getSysExchangeRateDetailResponse(JBSResponse):
    data: Optional[List[SysExchangeRateDetail]] = None


class getHrBaseResponse(JBSResponse):
    data: Optional[List[HRBase]] = None
