import json


def simplify_json(raw_json):
    # 载入json
    data = json.loads(raw_json)

    # 提取 columns 并建立 prop到列信息（科目、来源、年份等）映射
    prop_map = {}
    for col in data["data"]["columns"]:
        prop = col.get('prop')
        if prop:  # 排除subjectName列 只有label
            prop_map[prop] = {
                "year": col.get("labelYear"),
                "source": col.get("labelSource"),
                "type": col.get("labelType"),
            }

    # 定义输出
    simplified = []
    for row in data["data"]["data"]:
        simple_row = {'subjectName': row['subjectName']}
        for prop, value in row.items():
            if prop in prop_map:
                # 只保留val，且加上年份与来源作复合列
                col_name = f"{prop_map[prop]['year']}_{prop_map[prop]['source']}"
                try:
                    val = value.get('val')
                    simple_row[col_name] = val
                except Exception as e:
                    pass
        simplified.append(simple_row)

    return simplified
