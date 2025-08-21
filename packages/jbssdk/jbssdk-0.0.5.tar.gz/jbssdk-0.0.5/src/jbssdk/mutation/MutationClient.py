from datetime import datetime

import httpx
import markdown

from .Model.DeptAndUser import DeptAndUser, User
from .lib.processFile import chunk_binary_file
from .lib.processUser import processTreeDataToFlatWithLabel
from .. import timeout, limits
from ..BaseClient import JBSBaseClient


class JBSMutationClient(JBSBaseClient):
    async def findDeptAndUserByUserName(self, username):
        path = f'{self.BASEURL}/system/user/findDeptAndUserByUserName?userName={username}'
        async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
            result = await client.get(path, headers=await self.getGoodHeader())
            try:
                if result.status_code == 200:
                    return DeptAndUser.model_validate(result.json()['data'])
            except Exception as e:
                return None

    async def uploadFiles(self, fileName, binary):
        path = f'{self.BASEURL}/file/fileBase/uploadDocLib'
        params = {
            "dataType": "deal_base"
        }
        header = await self.getGoodHeader()
        result = None
        async for chunk in chunk_binary_file(binary, fileName, chunk_size=2048000):
            form_data = {
                "chunkNumber": chunk["chunkNumber"],
                "chunkSize": chunk["chunkSize"],
                "currentChunkSize": chunk["currentChunkSize"],
                "totalSize": chunk["totalSize"],
                "identifier": chunk["identifier"],
                "filename": chunk["filename"],
                "relativePath": chunk["relativePath"],
                "totalChunks": chunk["totalChunks"],
            }
            files = {
                "file": (fileName, chunk["file"])
            }
            async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
                res = await client.post(path, params=params, data=form_data, files=files, headers=header)
                try:
                    if res.status_code == 200:
                        if res.json()['data']['status'] == 'ALL':
                            return {
                                "identifier": chunk["identifier"],
                                "dataType": "deal_base",
                                "totalSize": chunk["totalSize"],
                                "originalFilename": fileName,
                                "totalChunks": chunk["totalChunks"],
                                "fileId": ""
                            }
                        else:
                            result = res.json()
                    else:
                        return None
                except Exception as e:
                    return None
        return result

    async def getCommonResultJsonData_POST(self, path, data):
        async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
            res = await client.post(path, json=data, headers=await self.getGoodHeader())
            try:
                if res.status_code == 200:
                    return res.json()['data']
            except Exception as e:
                return None

    async def getCommonResultJsonData_GET(self, path):
        async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
            res = await client.get(path, headers=await self.getGoodHeader())
            try:
                if res.status_code == 200:
                    return res.json()['data']
            except Exception as e:
                return None

    async def getHRBaseInternal(self):
        res = await self.getCommonResultJsonData_GET(f'{self.BASEURL}/base/internalBase/findInternal')
        return res

    async def getHRBaseContract(self, userId):
        res = await self.getCommonResultJsonData_GET(f'{self.BASEURL}/contract/hrBaseContract/{userId}')
        return res

    async def updateHrBaseContract(self, jsonData):
        res = await self.getCommonResultJsonData_POST(f'{self.BASEURL}/contract/hrBaseContract/save', jsonData)
        return res

    # 在职人员花名册 List
    async def getHRlist(self, pageNum, pageSize, status='zz'):
        async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
            queryparams = {
                "pageNum": pageNum,
                "pageSize": pageSize,
                'status': status
            }

            res = await client.get(f"{self.BASEURL}/hrBase/hrBase/list", params=queryparams,
                                   headers=self.getTokenHeader())
            try:
                if res.status_code == 200:
                    res =  res.json()
                    return [{
                        "hrId":r.get('id'),
                        "name":r.get('name'),
                        "userId":r.get('userId'),
                    } for r in res.get('rows')]
            except Exception as e:
                return None

    async def fileMerge(self, identifier, originalFilename, totalChunks, totalSize):
        path = f'{self.BASEURL}/file/fileBase/fileBaseMerging'
        json_data = {
            "identifier": identifier,
            "dataType": "deal_base",
            "totalSize": totalSize,
            "originalFilename": originalFilename,
            "totalChunks": totalChunks,
            "fileId": ""
        }
        return await self.getCommonResultJsonData_POST(path, json_data)

    async def syncNotes(self, dealId, details, userId):
        token = await self.loginToJBS()
        jsonData = {
            "user": {
                "userId": userId
            },
            "syncWeekly": "0",
            "dealId": dealId,
            "happenTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "itemType": "BPFXBG",
            "trackMode": "WX",
            "levelConcern": "B",
            "otherPeople": "",
            "workload": 10,
            "details": markdown.markdown(details),
            "nextStepPlan": "",
            "createBy": {
                "id": userId
            },
            "updateBy": {
                "id": userId
            }
        }
        async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
            res = await client.post(f'{self.BASEURL}/track/dealTrack/save', json=jsonData,
                                    headers=await self.getGoodHeader())
            try:
                if res.status_code == 200:
                    return res.json()
            except Exception as e:
                return None

    async def getAllUsers(self):
        token = await self.loginToJBS()
        BASE_URL = f'{self.BASEURL}/system/user/treeData'

        async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
            result = await client.get(BASE_URL, headers=await self.getGoodHeader())
            try:
                if result.status_code == 200:
                    return [User(**user_data) for user_data in result.json()['data']]
            except Exception as e:
                return None

    async def findUserNickNameByUserId(self, userId):
        UserLists = await self.getAllUsers()
        flatData = processTreeDataToFlatWithLabel(UserLists, None)
        for i in flatData:
            if i['userId'] == userId:
                return i['userName']
        return None

    async def findUserIdByNickName(self, NickName):
        UserLists = await self.getAllUsers()
        flatData = processTreeDataToFlatWithLabel(UserLists, None)
        for i in flatData:
            if i['userName'] == NickName:
                return i['userId']
        return None

    async def AddProject(self, companyName, dealName, userName, filelist, business_introduction, partnerLabel,
                         financing_amount, financing_currency,
                         financing_round,
                         invest_before_valuation, invest_after_valuation):
        """

        :param companyName:
        :param dealName:
        :param userName:
        :param filelist:
        :param business_introduction:
        :param partnerLabel: ref src/jbssdk/mutation/consts/Partners.py
        :param financing_amount:
        :param financing_currency:
        :param financing_round:
        :param invest_before_valuation:
        :param invest_after_valuation:
        :return:
        """
        code = "a49c098e97de47188939e0881da71ddb"
        path = f'{self.BASEURL}/head/OnlineApiTest/api/formAdd/{code}'
        userInfo = await self.findDeptAndUserByUserName(userName)
        dealIndustry = userInfo['deptKey']
        userId = userInfo['userId']
        dataJson = {
            "company_id": companyName,
            "deal_name": dealName,
            "deal_status": "CB",  # 默认是储备状态
            "deal_type": "equity",
            "source_type": "Proprietory",
            "person_charge": userId,
            "deal_industry": dealIndustry,
            "staff": userId,  # 推荐员工
            "deal_team_members": [userId],  # 团队成员
            "filelist": filelist,
            "create_by": userId,
            "business_introduction": business_introduction,  # 介绍
            "partener_label": partnerLabel,
            "strategy_buddy": partnerLabel,
        }

        if financing_amount is not None:
            dataJson["financing_amount"] = financing_amount
        if financing_currency is not None:
            dataJson["financing_currency"] = financing_currency
        if financing_round is not None:
            dataJson["financing_round"] = financing_round
        if invest_before_valuation is not None:
            dataJson["invest_before_valuation"] = invest_before_valuation
        if invest_after_valuation is not None:
            dataJson["invest_after_valuation"] = invest_after_valuation
        return await self.getCommonResultJsonData_POST(path, dataJson)
