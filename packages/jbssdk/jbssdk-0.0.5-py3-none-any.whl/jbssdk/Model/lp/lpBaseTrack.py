from typing import Optional

from pydantic import BaseModel


class LPBaseTrack(BaseModel):
    """
    lpId	投资人ID
lpName	投资人名称
happenType	事件发生类型
happenDate	发生时间
trackMode	跟踪方式
fundName	相关募集基金
otherPeople	对方人员
ourPerson	我方人员
updateBy	更新人
updateTime	更新时间
remark	详细情况
nextPlan	下一步计划
    """
    lpId: Optional[str] = None
    lpName: Optional[str] = None
    happenType: Optional[str] = None
    happenDate: Optional[str] = None
    trackMode: Optional[str] = None
    fundName: Optional[str] = None
    otherPeople: Optional[str] = None
    ourPerson: Optional[str] = None
    updateBy: Optional[str] = None
    updateTime: Optional[str] = None
    remark: Optional[str] = None
    nextPlan: Optional[str] = None
