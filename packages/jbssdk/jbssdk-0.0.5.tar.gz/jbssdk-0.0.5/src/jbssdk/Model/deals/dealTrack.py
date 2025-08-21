from typing import Optional

from pydantic import BaseModel


class DealBeforeTrack(BaseModel):
    """
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
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    createBy: Optional[str] = None
    createTime: Optional[str] = None
    happenTime: Optional[str] = None
    itemType: Optional[str] = None
    trackMode: Optional[str] = None
    otherPeople: Optional[str] = None
    details: Optional[str] = None
