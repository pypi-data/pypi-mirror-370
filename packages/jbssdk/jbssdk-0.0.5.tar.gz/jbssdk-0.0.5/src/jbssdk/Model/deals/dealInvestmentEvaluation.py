from typing import Optional

from pydantic import BaseModel


class DealAfterInvestEvaluation(BaseModel):
    """
项目ID                        \n
项目名称                        \n
创建人                         \n
发生时间                        \n
评价类型                        \n
发展近况                        \n
下一步行动及重点                    \n
    """
    dealId: Optional[str] = None
    dealName: Optional[str] = None
    createBy: Optional[str] = None
    happenTime: Optional[str] = None
    itemType: Optional[str] = None
    recentDevelopments: Optional[str] = None
    nextPlan: Optional[str] = None
    companyId: Optional[str] = None
    companyName: Optional[str] = None
