from typing import Optional

from pydantic import BaseModel


class HRBase(BaseModel):
    """
    userName	关联系统用户
name	姓名
sex	性别
birthDate	出生年月
idType	证件类型
idNum	证件号码
age	年龄
nation	民族
deptName	所在部门
politicalOutlook	政治面貌
position	职位
entryTime	入职时间
staffType	员工类型
workingYear	工作年限
censusRegisterType	户籍类型
censusRegisterAddress	户籍所在地
currentAddress	现住地
contractType	合同或协议类型
international	国籍
marriage	婚姻状况
email	个人邮箱
companyEmail	公司邮箱
phone	手机号码
takeEffectTime	合同或协议生效时间
terminationTime	合同或协议终止时间
contractTerm	合同或协议期限
renewalTime	续签时间
positiveTime	转正时间
status	状态
quitTime	离职时间
openingBank	开户行
bankCardNumber	银行卡号
goodAtField	擅长领域
investmentPhilosophy	投资理念
excellentInvestmentCase	优秀投资案例
honours	所获荣誉

    """
    userName: Optional[str] = None
    name: Optional[str] = None
    sex: Optional[str] = None
    birthDate: Optional[str] = None
    idType: Optional[str] = None
    idNum: Optional[str] = None
    age: Optional[int] = None
    nation: Optional[str] = None
    deptName: Optional[str] = None
    politicalOutlook: Optional[str] = None
    position: Optional[str] = None
    entryTime: Optional[str] = None
    staffType: Optional[str] = None
    workingYear: Optional[str] = None
    censusRegisterType: Optional[str] = None
    censusRegisterAddress: Optional[str] = None
    currentAddress: Optional[str] = None
    contractType: Optional[str] = None
    international: Optional[str] = None
    marriage: Optional[str] = None
    email: Optional[str] = None
    companyEmail: Optional[str] = None
    phone: Optional[str] = None
    takeEffectTime: Optional[str] = None
    terminationTime: Optional[str] = None
    contractTerm: Optional[str] = None
    renewalTime: Optional[str] = None
    positiveTime: Optional[str] = None
    status: Optional[str] = None
    quitTime: Optional[str] = None
    openingBank: Optional[str] = None
    bankCardNumber: Optional[str] = None
    goodAtField: Optional[str] = None
    investmentPhilosophy: Optional[str] = None
    excellentInvestmentCase: Optional[str] = None
    honours: Optional[str] = None
