from typing import Optional

from pydantic import BaseModel


class SysExchangeRateDetail(BaseModel):
    toCurrency: Optional[str] = None
    toCurrencyLabel: Optional[str] = None
    fromCurrency: Optional[str] = None
    fromCurrencyLabel: Optional[str] = None
    exchangeRate: Optional[float] = None
    exchangeDate: Optional[str] = None
