from typing import Optional, List

from pydantic import BaseModel


class DeptAndUser(BaseModel):
    deptKey: Optional[str] = None
    deptId: Optional[str] = None
    userId: Optional[str] = None


class User(BaseModel):
    id:Optional[str]=None
    parentId:Optional[str]=None
    label:Optional[str]=None
    open:Optional[bool]=None
    choose:Optional[bool]=None
    deptOrUser:Optional[str]=None
    disabled:Optional[bool]=None
    children: Optional[List['User']] = None