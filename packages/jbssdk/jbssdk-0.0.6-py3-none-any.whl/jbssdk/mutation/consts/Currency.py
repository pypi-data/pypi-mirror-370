class Currency:
    CNY = "CNY"  # 人民币
    USD = "USD"  # 美元
    EUR = "EUR"  # 欧元
    JPY = "JPY"  # 日元
    GBP = "GBP"  # 英镑
    KRW = "KRW"  # 韩元
    HKD = "HKD"  # 港元
    AUD = "AUD"  # 澳大利亚元
    CAD = "CAD"  # 加拿大元
    @classmethod
    def get_all_currencies(cls):
        currencies = []
        for key, value in cls.__dict__.items():
            # 过滤掉内置属性和方法
            if not key.startswith("__") and not callable(value):
                currencies.append(value)
        return currencies