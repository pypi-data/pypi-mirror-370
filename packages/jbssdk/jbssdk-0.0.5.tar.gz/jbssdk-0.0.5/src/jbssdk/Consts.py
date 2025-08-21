class JBSCode:
    DEAL_BEFORE_INFO = "deal_before_info"  # 投前


class JBSConst:
    isPage = "isPage"
    """
    #（是否需要分页）可选值true-需要分页｜false-不需要分页（默认为false）
    """
    pageNum = "pageNum"
    """
    （页码）isPage为true时，如果不传入，默认为第一页
    """
    pageSize = "pageSize"
    """
    （每页条数）isPage为true时，如果不传入，默认为10条
    """