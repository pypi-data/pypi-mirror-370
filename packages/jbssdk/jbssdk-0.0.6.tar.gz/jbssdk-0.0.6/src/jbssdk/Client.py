import json
import os
from typing import Type, Literal

import dotenv
import httpx

from . import timeout, limits
from .BaseClient import JBSBaseClient
from .Model.Response import *
from .Model.inner_api.BaseParams import InnerPayLoad

dotenv.load_dotenv()



class JBS(JBSBaseClient):
    # 首页看板专用
    async def _innerAPIDashBoardViewResponse(self, InnerPayload: InnerPayLoad) -> Optional[
        innerAPIDashBoardViewResponse]:
        async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
            try:
                resp = await client.post(f'{self.BASEURL}/view/searchMainView/getDataListByView',
                                         json=InnerPayload.model_dump(), headers=await self.getGoodHeader())
                # 检查响应状态码，抛出异常如果请求失败
                resp.raise_for_status()
                # 返回 JSON 格式的响应数据
                if os.getenv('SHOULDPRINT') == "1":
                    print(json.dumps(resp.json(), ensure_ascii=False))
                return innerAPIDashBoardViewResponse(**resp.json())
            except httpx.HTTPStatusError as e:
                # 处理 HTTP 状态错误（如 404, 500 等）
                print(f"HTTP error occurred: {e}")
                return None
            except httpx.RequestError as e:
                # 处理请求相关错误（如网络问题）
                print(f"Request error occurred: {e}")
                return None
            except Exception as e:
                # 捕获其他未预料到的异常
                print(f"Unexpected error occurred: {e}")
                return None

    async def _innerAPICommpnResponse(self, query_params, basePath: str) -> Optional[innerAPICommonResponse]:
        async with httpx.AsyncClient(limits=limits, timeout=timeout, verify=False) as client:
            try:
                # 发送 GET 请求，并传递查询参数
                response = await client.get(
                    url=f'{self.BASEURL}/{basePath}',
                    params=query_params,
                    headers=await self.getGoodHeader()
                )
                # 检查响应状态码，抛出异常如果请求失败
                response.raise_for_status()
                # 返回 JSON 格式的响应数据
                if os.getenv('SHOULDPRINT') == "1":
                    print(json.dumps(response.json(), ensure_ascii=False))
                return innerAPICommonResponse(**response.json())
                # return response.json()
            except httpx.HTTPStatusError as e:
                # 处理 HTTP 状态错误（如 404, 500 等）
                print(f"HTTP error occurred: {e}")
                return None
            except httpx.RequestError as e:
                # 处理请求相关错误（如网络问题）
                print(f"Request error occurred: {e}")
                return None
            except Exception as e:
                # 捕获其他未预料到的异常
                print(f"Unexpected error occurred: {e}")
                return None

    async def _commonResponse(self, query_params, Model: Type[T]) -> Optional[T]:
        async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
            try:
                # 发送 GET 请求，并传递查询参数
                response = await client.get(
                    url=self.COMPLETION_URL,
                    params=query_params,
                    headers=await self.getGoodHeader()
                )
                # 检查响应状态码，抛出异常如果请求失败
                response.raise_for_status()
                # 返回 JSON 格式的响应数据
                if os.getenv('SHOULDPRINT') == "1":
                    print(json.dumps(response.json(), ensure_ascii=False))
                return Model(**response.json())
                # return response.json()
            except httpx.HTTPStatusError as e:
                # 处理 HTTP 状态错误（如 404, 500 等）
                print(f"HTTP error occurred: {e}")
                return None
            except httpx.RequestError as e:
                # 处理请求相关错误（如网络问题）
                print(f"Request error occurred: {e}")
                return None
            except Exception as e:
                # 捕获其他未预料到的异常
                print(f"Unexpected error occurred: {e}")
                return None

    async def get_deal_before_info(self, dealId: str = None, dealName: str = None, companyName: str = None,
                                   startTime: str = None, endTime: str = None):
        """
            投前信息
        """
        query_params = self.build_query_params(
            dealId=dealId,
            dealName=dealName,
            companyName=companyName,
            startTime=startTime,
            endTime=endTime,
            code='deal_before_info'
        )
        return await self._commonResponse(query_params, getDealBeforeInfoResponse)

    async def get_deal_before_track(self, dealId=None, dealName=None, startTime=None, endTime=None) -> Optional[
        getDealBeforeTrackTrackResponse]:
        """
        2.项目跟踪
        :param dealId: 项目ID
        :param dealName:项目名称
        :param startTime:项目跟踪开始时间
        :param endTime:项目跟踪结束时间
        :return:
        dealId	项目ID
        dealName	项目名称
        createBy	创建人
        createTime	创建时间
        happenTime	发生时间
        itemType	事项类型
        trackMode	跟踪方式
        otherPeople	对方人员
        details	详细情况
        """
        query_params = self.build_query_params(code='deal_before_track', dealId=dealId, dealName=dealName,
                                               startTime=startTime, endTime=endTime)
        return await self._commonResponse(query_params, getDealBeforeTrackTrackResponse)

    async def get_deal_before_meeting(self, dealId=None, dealName=None, startTime=None, endTime=None, fundName=None):
        """
        项目上会数据
        :param dealId:项目ID
        :param dealName:项目名称
        :param startTime:会议日期开始时间
        :param endTime:会议日期结束时间
        :param fundName:投资主体名称
        :return:
        daelId	项目ID
        dealName	项目名称
        meetingType	上会类型
        fundName	投资主体
        investAmount	预计投资金额
        investCurrency	投资币种
        actTitle	申请标题
        applyContent	申请内容
        mtDate	会议日期
        mtTime	会议时间
        mtConclusion	会议结论
        mtComment	会议纪要邮件正文
        """
        query_params = self.build_query_params(code='deal_before_meeting', dealId=dealId, dealName=dealName,
                                               startTime=startTime, endTime=endTime, fundName=fundName)
        return await self._commonResponse(query_params, getDealBeforeMeetingResponse)

    async def get_deal_after_info(self, dealId: str = None, dealName: str = None, companyName: str = None,
                                  startTime: str = None, endTime: str = None):
        """
            投后信息
        """
        query_params = self.build_query_params(
            dealId=dealId,
            dealName=dealName,
            companyName=companyName,
            startTime=startTime,
            endTime=endTime,
            code='deal_after_info'
        )
        return await self._commonResponse(query_params, getDealAfterInfoResponse)

    async def get_deal_after_investment(self, dealId=None, dealName=None, investmentName=None):
        query_params = self.build_query_params(code='deal_after_investment', dealId=dealId, dealName=dealName,
                                               investmentName=investmentName)
        return await self._commonResponse(query_params, getDealAfterInvestmentResponse)

    async def get_deal_after_terms(self, dealId=None, dealName=None, termsType=None):
        """
        项目关键条款
        :param termsType:
        :param dealId:
        :param dealName:
        :return:
        """
        query_params = self.build_query_params(code='deal_after_terms', dealId=dealId, dealName=dealName,
                                               termsType=termsType
                                               )

        return await self._commonResponse(query_params, getDealAfterTermsResponse)

    async def get_deal_after_pcw(self,
                                 dealId=None,
                                 dealName=None,
                                 companyId=None,
                                 companyName=None,
                                 pcwTableType=None,
                                 dataSource=None,
                                 year=None,
                                 reportingPeriod=None,
                                 keyName=None,
                                 pageNum=None,
                                 pageSize=None,
                                 isPage="false",
                                 ):
        """
        项目财务数据
        :param pageNum:
        :param pageSize:
        :param isPage:
        :param dealId:                                 项目ID
        :param dealName:                               项目名称
        :param companyId:                              公司ID
        :param companyName:                            公司名称
        :param pcwTableType:                           财务数据类型
        :param dataSource:                             数据来源
        :param year:                                   报告年份
        :param reportingPeriod:                        报告周期
        :param keyName:                                财务指标
        :return:
        """
        query_params = self.build_query_params(code='deal_after_pcw', dealId=dealId,
                                               dealName=dealName,
                                               companyId=companyId,
                                               companyName=companyName,
                                               pcwTableType=pcwTableType,
                                               dataSource=dataSource,
                                               year=year,
                                               reportingPeriod=reportingPeriod,
                                               keyName=keyName, pageNum=pageNum, pageSize=pageSize, isPage=isPage)
        return await self._commonResponse(query_params, getDealAfterPCWResponse)

    async def get_deal_after_pcw_key_indicator_data(self,
                                                    dealId=None,
                                                    dealName=None,
                                                    companyId=None,
                                                    companyName=None,
                                                    pcwTableType=None,
                                                    dataSource=None,
                                                    year=None,
                                                    reportingPeriod=None,
                                                    keyName=None,
                                                    pageNum=None,
                                                    pageSize=None,
                                                    isPage=None,
                                                    ):
        """
        项目财务数据
        :param isPage:
        :param pageSize:
        :param pageNum:
        :param dealId:                                 项目ID
        :param dealName:                               项目名称
        :param companyId:                              公司ID
        :param companyName:                            公司名称
        :param pcwTableType:                           财务数据类型
        :param dataSource:                             数据来源
        :param year:                                   报告年份
        :param reportingPeriod:                        报告周期
        :param keyName:                                财务指标
        :return:
        """
        query_params = self.build_query_params(code='deal_after_pcw_key_indicator_data', dealId=dealId,
                                               dealName=dealName,
                                               companyId=companyId,
                                               companyName=companyName,
                                               pcwTableType=pcwTableType,
                                               dataSource=dataSource,
                                               year=year,
                                               reportingPeriod=reportingPeriod,
                                               keyName=keyName, pageNum=pageNum, pageSize=pageSize, isPage=isPage)
        return await self._commonResponse(query_params, getDealAfterPCWResponse)

    async def get_deal_after_captable(self,
                                      dealId=None,
                                      dealName=None,
                                      companyName=None,
                                      startTime=None,
                                      endTime=None,
                                      ):
        """
        4.项目Captable数据
        :param dealId:
        :param dealName:
        :param companyName:
        :param startTime:融资日期开始时间
        :param endTime:融资日期结束时间
        :return:
        """
        query_params = self.build_query_params(code='deal_after_captable', dealId=dealId,
                                               dealName=dealName,
                                               companyName=companyName,
                                               startTime=startTime,
                                               endTime=endTime)
        return await self._commonResponse(query_params, getDealAfterCaptableResponse)

    async def get_deal_after_captable_detail(self,
                                             dealId=None,
                                             dealName=None,
                                             companyName=None,
                                             changeId=None
                                             ):
        """
        5.项目Captable数据-股权变更详情
        :param dealId:
        :param dealName:
        :param companyName:
        :param changeId: 即captabelId
        :return:
        """
        query_params = self.build_query_params(code='deal_after_captabel_detail', dealId=dealId,
                                               dealName=dealName,
                                               companyName=companyName,
                                               changeId=changeId)
        return await self._commonResponse(query_params, getDealAfterCaptableDetailResponse)

    async def get_deal_after_invest_evaluation(self,
                                               dealId=None,
                                               dealName=None,
                                               companyName=None,
                                               startTime=None,
                                               endTime=None
                                               ):
        query_params = self.build_query_params(code='deal_after_invest_evaluation',
                                               dealId=dealId,
                                               dealName=dealName,
                                               companyName=companyName,
                                               startTime=startTime,
                                               endTime=endTime
                                               )
        return await self._commonResponse(query_params, getDealAfterInvestEvaluationResponse)

    async def get_deal_after_cashflow(self,
                                      dealId=None,
                                      dealName=None,
                                      startTime=None,
                                      endTime=None,
                                      ):
        """
        现金流
        :param dealId:
        :param dealName:
        :param startTime:发生时间开始时间
        :param endTime:发生时间结束时间
        :return:
        """
        query_params = self.build_query_params(code='deal_after_cashflow', dealId=dealId,
                                               dealName=dealName,
                                               startTime=startTime,
                                               endTime=endTime)
        return await self._commonResponse(query_params, getDealAfterCashFlowResponse)

    async def get_deal_after_valuation(self,
                                       dealId=None,
                                       dealName=None,
                                       startTime=None,
                                       endTime=None,
                                       ):
        query_params = self.build_query_params(code='deal_after_valuation', dealId=dealId,
                                               dealName=dealName,
                                               startTime=startTime,
                                               endTime=endTime, )
        return await self._commonResponse(query_params, getDealAfterValuationResponse)

    async def get_deal_after_valuation_investment(self,
                                                  dealId=None,
                                                  dealName=None,
                                                  valuationId=None,
                                                  ):
        query_params = self.build_query_params(code='deal_after_valuation_investment', dealId=dealId,
                                               dealName=dealName,
                                               valuationId=valuationId, )
        return await self._commonResponse(query_params, getDealAfterValuationInvestmentResponse)

    async def get_fund_base_info(self, fundId=None, fundName=None, fundFullName=None):
        """
        基金基本信息
        :param fundId:
        :param fundName:
        :param fundFullName:
        :return:
        """
        query_params = self.build_query_params(
            code='fund_base_info',
            fundId=fundId,
            fundName=fundName,
            fundFullName=fundFullName
        )
        return await self._commonResponse(query_params, getFundBaseInfoResponse)

    async def get_fund_base_info_parse(self, fundId=None,
                                       fundName=None,
                                       fundFullName=None):
        query_params = self.build_query_params(code='fund_base_info_phase', fundId=fundId,
                                               fundName=fundName,
                                               fundFullName=fundFullName)
        return await self._commonResponse(query_params, getFundBaseInfoPhaseResponse)

    async def get_fund_base_investor(self, fundId=None,
                                     fundName=None,
                                     investorName=None):
        query_params = self.build_query_params(code='fund_base_investor', fundId=fundId,
                                               fundName=fundName,
                                               investorName=investorName)
        return await self._commonResponse(query_params, getFundBaseInvestorResponse)

    async def get_fund_base_investor_lpa(self, fundId=None,
                                         fundName=None,
                                         investorName=None):
        """
            出资人LPA关键条款
        :param fundId:
        :param fundName:
        :param investorName:
        :return:
        """
        query_params = self.build_query_params(code='fund_base_investor_lpa', fundId=fundId,
                                               fundName=fundName,
                                               investorName=investorName)
        return await self._commonResponse(query_params, getFundBaseInvestorLPAResponse)

    async def get_fund_base_cash_flow(self,
                                      fundId=None,
                                      fundName=None,
                                      startTime=None,
                                      endTime=None,
                                      ):
        """
        基金现金流
        :param fundId:
        :param fundName:
        :param startTime:
        :param endTime:
        :return:
        """
        query_params = self.build_query_params(code='fund_base_cashflow',
                                               fundId=fundId,
                                               fundName=fundName,
                                               startTime=startTime,
                                               endTime=endTime,
                                               )
        return await self._commonResponse(query_params, getFundBaseCashFlowResponse)

    async def get_fund_base_lp_cashflow(self,
                                        fundId=None,
                                        fundName=None,
                                        lpName=None,
                                        startTime=None,
                                        endTime=None,
                                        ):
        query_params = self.build_query_params(code='fund_base_lp_cashflow',
                                               fundId=fundId,
                                               fundName=fundName,
                                               startTime=startTime,
                                               endTime=endTime,
                                               lpName=lpName
                                               )
        return await self._commonResponse(query_params, getFundBaseLPCashFlowResponse)

    async def get_fund_base_valuation(self,
                                      fundId=None,
                                      fundName=None,
                                      startTime=None,
                                      endTime=None
                                      ):
        """
        基金估值数据
        :param fundId:
        :param fundName:
        :param startTime:
        :param endTime:
        :return:
        """
        query_params = self.build_query_params(code='fund_base_valuation', fundId=fundId,
                                               fundName=fundName,
                                               startTime=startTime,
                                               endTime=endTime)
        return await self._commonResponse(query_params, getFundBaseValuationResponse)

    async def get_fund_base_expense(self, fundId=None, fundName=None, startTime=None, endTime=None):
        query_params = self.build_query_params(code='fund_base_expense', fundId=fundId, fundName=fundName,
                                               startTime=startTime, endTime=endTime)
        return await self._commonResponse(query_params, getFundBaseExpenseResponse)

    async def get_fund_base_income(self, fundId=None,
                                   fundName=None,
                                   dealName=None,
                                   startTime=None,
                                   endTime=None
                                   ):
        query_params = self.build_query_params(code='fund_base_income',
                                               fundId=fundId,
                                               fundName=fundName,
                                               dealName=dealName,
                                               startTime=startTime,
                                               endTime=endTime
                                               )
        return await self._commonResponse(query_params, getFundBaseIncomeResponse)

    async def get_lp_base_info(self, lpId=None,
                               lpName=None):
        query_params = self.build_query_params(code='lp_base_info', lpId=lpId, lpName=lpName)
        return await self._commonResponse(query_params, getLPBaseInfoResponse)

    async def get_lp_base_track(self,
                                lpId=None,
                                lpName=None,
                                startTime=None,
                                endTime=None,
                                ):
        query_params = self.build_query_params(code='lp_base_track', lpId=lpId,
                                               lpName=lpName,
                                               startTime=startTime,
                                               endTime=endTime)
        return await self._commonResponse(query_params, getLPBaseTrackResponse)

    async def get_lp_base_investor(self, lpId=None,
                                   lpName=None,
                                   startTime=None,
                                   endTime=None, ):
        query_params = self.build_query_params(code='lp_base_investor', lpId=lpId,
                                               lpName=lpName,
                                               startTime=startTime,
                                               endTime=endTime)
        return await self._commonResponse(query_params, getLPBaseInvestorResponse)

    async def get_gp_base_info(self,
                               gpId=None,
                               gpName=None,
                               gpShortName=None,
                               ):
        query_params = self.build_query_params(code='gp_base_info', gpId=gpId,
                                               gpName=gpName,
                                               gpShortName=gpShortName, )
        return await self._commonResponse(query_params, getGPBaseInfoResponse)

    async def get_gp_base_fund(self, gpId=None,
                               gpName=None,
                               type=None,
                               fundId=None,
                               fundName=None):
        query_params = self.build_query_params(code='gp_base_fund', gpId=gpId,
                                               gpName=gpName,
                                               type=type,
                                               fundId=fundId,
                                               fundName=fundName)
        return await self._commonResponse(query_params, getGPBaseFundResponse)

    async def getDealInFund(self, fundName, stage, pageNum=1, pageSize=50):
        searchQueryVoList_ = []
        if fundName:
            searchQueryVoList_.append({
                "value": fundName,
                "fieldName": "投资主体",
                "conditions": "HDY",
                "type": "WB",
                "date": "",
                "group": True
            })
        if stage:
            searchQueryVoList_.append({
                "conditions": "HDY",
                "fieldName": "项目阶段",
                "group": True,
                "type": "WB",
                "date": "",
                "value": stage,
            })
        payload = {
            "pageSize": pageSize,
            "pageNum": pageNum,
            "paramsMap": {},
            "searchOrderByVo": {
                "prop": "项目名称",
                "order": "ascending"
            },
            "searchQueryVoList": searchQueryVoList_,
            "viewId": "514ed3b5fa9745be8445ae504dd5447d"
        }
        return await self._innerAPIDashBoardViewResponse(InnerPayLoad(**payload))

    async def getPCWList(self, companyId, belongsTable: Optional[
        Literal['balance_sheet', 'income_sheet', 'cash_flow_sheet']] = 'balance_sheet', pageNum=None, pageSize=None,
                         type=None, yearS=None, yearE=None):
        query_params = self.build_query_params(
            companyId=companyId, belongsTable=belongsTable, pageNum=pageNum, pageSize=pageSize, type=type, yearS=yearS,
            yearE=yearE
        )
        basePath = 'pcw/pcwDataBase/listGroup'
        return await self._innerAPICommpnResponse(query_params, basePath)

    async def get_fund_base_deal_cashflow(self, fundId=None, fundName=None, startTime=None, endTime=None):
        query_params = self.build_query_params(code='fund_base_deal_cashflow', fundId=fundId, fundName=fundName,
                                               startTime=startTime, endTime=endTime)
        return await self._commonResponse(query_params, getFundBaseDealCashFlowResponse)

    async def get_sys_exchange_rate(self, ):
        query_params = self.build_query_params(code='sys_exchange_rate')
        return await self._commonResponse(query_params, getSysExchangeRateResponse)

    async def get_sys_exchange_rate_detail(self, toCurrencyLabel, fromCurrencyLabel, exchangeDate=None):
        query_params = self.build_query_params(code='sys_exchange_rate_detail', fromCurrencyLabel=fromCurrencyLabel,
                                               toCurrencyLabel=toCurrencyLabel, exchangeDate=exchangeDate)
        return await self._commonResponse(query_params, getSysExchangeRateDetailResponse)

    async def get_deal_after_exit_strategy(self, dealId=None,
                                           dealName=None):
        query_params = self.build_query_params(code='deal_after_exit_strategy', dealId=dealId, dealName=dealName)
        return await self._commonResponse(query_params, getDealAfterExitStrategyResponse)

    async def get_deal_after_cathay_case_initial(self, dealId=None,
                                                 dealName=None,
                                                 investmentId=None,
                                                 investmentName=None):
        query_params = self.build_query_params(code='deal_after_cathay_case_initial', dealId=dealId, dealName=dealName,
                                               investmentName=investmentName, investmentId=investmentId)
        return await self._commonResponse(query_params, getDealAfterCathayCaseInitialResponse)

    async def get_deal_after_cathay_case_revised(self, dealId=None,
                                                 dealName=None,
                                                 investmentId=None,
                                                 investmentName=None):
        query_params = self.build_query_params(code='deal_after_cathay_case_reviesed', dealId=dealId, dealName=dealName,
                                               investmentName=investmentName, investmentId=investmentId)
        return await self._commonResponse(query_params, getDealAfterCathayCaseRevisedResponse)

    async def get_deal_after_investment_case_detail(self, cathayCaseId=None):
        query_params = self.build_query_params(code='deal_after_investment_case_detail', cathayCaseId=cathayCaseId)
        return await self._commonResponse(query_params, getDealAfterInvestmentCaseDetailResponse)

    async def get_hr_base(self, name=None,
                          status=None,
                          deptName=None,
                          position=None):
        query_params = self.build_query_params(code='hr_base', name=name, status=status, deptName=deptName,
                                               position=position)
        return await self._commonResponse(query_params, getHrBaseResponse)
