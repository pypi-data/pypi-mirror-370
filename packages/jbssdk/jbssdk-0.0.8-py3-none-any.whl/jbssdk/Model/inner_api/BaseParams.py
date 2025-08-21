from enum import Enum
from typing import Any

from pydantic import BaseModel


class OrderEnum(str, Enum):
    ascending = "ascending"
    descending = "descending"


class searchOrderByVo(BaseModel):
    order: OrderEnum
    prop: str


class searchQueryVo(BaseModel):
    conditions: str
    date: str
    fieldName: str
    type: str
    value: str


class InnerPayLoad(BaseModel):
    pageNum: int
    pageSize: int
    paramsMap:Any
    searchOrderByVo: searchOrderByVo
    searchQueryVoList: list[searchQueryVo]
    viewId: str
