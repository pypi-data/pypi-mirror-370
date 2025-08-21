class FundingRound:
    ZZL = "ZZL"
    TSL = "TSL"
    PREA = "PREA"
    A = "A"
    AJL = "AJL"
    B = "B"
    BJL = "BJL"
    B_PLUS_PLUS = "B_PLUS_PLUS"
    C = "C"
    CJL = "CJL"
    D = "D"
    E = "E"
    F = "F"
    PREXSB = "PREXSB"
    PREIPO = "PREIPO"
    IPO = "IPO"
    DZ = "DZ"

    CHINESE_TO_ABBREVIATION = {
        "种子轮": ZZL,
        "天使轮": TSL,
        "Pre-A": PREA,
        "A轮": A,
        "A+轮": AJL,
        "B轮": B,
        "B+轮": BJL,
        "B++轮": B_PLUS_PLUS,
        "C轮": C,
        "C+轮": CJL,
        "D轮": D,
        "E轮": E,
        "F轮": F,
        "Pre-新三板": PREXSB,
        "Pre-IPO": PREIPO,
        "IPO": IPO,
        "定增": DZ
    }

    ABBREVIATION_TO_CHINESE = {v: k for k, v in CHINESE_TO_ABBREVIATION.items()}
