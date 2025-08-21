class Partners:
    # Existing and Verified Partners
    Ushopal = "Ushopal"
    Ushopal_ZH = "优商派"
    Sony = "Sony"
    Sony_ZH = "索尼"
    BNP_Paribas = "BNP Paribas"
    BNP_Paribas_ZH = "法国巴黎银行"
    ADP_Aeroports_de_Paris = "Aéroports de Paris"
    ADP_Aeroports_de_Paris_ZH = "法国巴黎机场"
    Accor = "Accor"
    Accor_ZH = "雅高集团"
    MACSF = "Mutuelle d'assurance du corps de santé français"
    MACSF_ZH = "法国医疗互助保险公司"
    Michelin = "Michelin"
    Michelin_ZH = "米其林"
    Swire = "Swire Group"
    Swire_ZH = "太古集团"
    Pierre_Fabre = "Pierre Fabre"
    Pierre_Fabre_ZH = "皮尔·法伯"
    Bpifrance = "Bpifrance"
    Bpifrance_ZH = "法国公共投资银行"
    Valeo = "Valeo"
    Valeo_ZH = "法雷奥"
    Schaeffler = "Schaeffler Group"
    Schaeffler_ZH = "舍弗勒集团"
    Air_Liquide = "Air Liquide"
    Air_Liquide_ZH = "液化空气集团"
    Vale = "Vale"
    Vale_ZH = "淡水河谷"
    CMA_CGM = "CMA CGM"
    CMA_CGM_ZH = "达飞海运"
    BNP_Paribas_Cardif = "BNP Paribas Cardif"
    BNP_Paribas_Cardif_ZH = "法国巴黎银行卡迪夫"
    BioMerieux = "bioMérieux"
    BioMerieux_ZH = "生物梅里埃"
    Kering = "Kering"
    Kering_ZH = "开云集团"
    Pernod_Ricard = "Pernod Ricard"
    Pernod_Ricard_ZH = "保乐力加"
    Sanofi = "Sanofi"
    Sanofi_ZH = "赛诺菲"
    TotalEnergies = "TotalEnergies"
    TotalEnergies_ZH = "道达尔能源"
    Unilever = "Unilever"
    Unilever_ZH = "联合利华"
    Anta = "Anta"
    Anta_ZH = "安踏"
    Joyoung = "Joyoung"
    Joyoung_ZH = "九阳"
    M6_Groupe = "Groupe M6"
    M6_Groupe_ZH = "M6集团"
    Creadev = "Creadev"
    Creadev_ZH = "克雷德夫"
    JCDecaux = "JCDecaux"
    JCDecaux_ZH = "德高广告"
    Ledger = "Ledger"
    Ledger_ZH = "莱杰"
    LOreal = "L'Oréal"
    LOreal_ZH = "欧莱雅"
    Tethys_Invest = "Tethys Invest"
    Tethys_Invest_ZH = "泰西斯"
    Tencent = "Tencent"
    Tencent_ZH = "腾讯"
    Groupe_SEB = "Groupe SEB"
    Groupe_SEB_ZH = "赛博集团"
    Neom = "Neom"
    Neom_ZH = "尼奥姆"

    @classmethod
    def get_partners(cls):
        partners_dict = {}
        for key, value in cls.__dict__.items():
            # 过滤掉内置属性和方法，以及中文变量
            if not key.startswith("__") and not callable(value) and not key.endswith("_ZH"):
                partners_dict[key] = value
        return partners_dict

    @classmethod
    def get_partners_zh(cls):
        partners_zh_dict = {}
        for key, value in cls.__dict__.items():
            # 过滤掉内置属性和方法，只保留中文变量
            if not key.startswith("__") and not callable(value) and key.endswith("_ZH"):
                partners_zh_dict[key] = value
        return partners_zh_dict

