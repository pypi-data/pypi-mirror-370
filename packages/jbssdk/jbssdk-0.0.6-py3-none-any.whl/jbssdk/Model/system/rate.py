from typing import Optional

from pydantic import BaseModel


class SysExchangeRate(BaseModel):
    toCurrency: Optional[str] = None
    toCurrencyLabel: Optional[str] = None
    fromCurrency: Optional[str] = None
    fromCurrencyLabel: Optional[str] = None
    exchangeRate: Optional[float] = None
    updateTime: Optional[str] = None
