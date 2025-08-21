from typing import List

from ..Model.DeptAndUser import User


def processTreeDataToFlat(UserLists: List[User]) -> List[User]:
    res = []
    for user in UserLists:
        if user.children is None:
            res.append(user)
        else:
            res.extend(processTreeDataToFlat(user.children))
    return res


def processTreeDataToFlatWithLabel(UserLists: List[User], parentLabel=None):
    res = []
    for user in UserLists:
        if user.children is None:
            res.append({
                "userId": user.id,
                "userName": user.label,
                "parentLabel": parentLabel
            })
        else:
            res.extend(processTreeDataToFlatWithLabel(user.children, user.label))
    return res
