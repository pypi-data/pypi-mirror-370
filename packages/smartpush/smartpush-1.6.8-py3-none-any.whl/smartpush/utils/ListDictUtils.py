import json

from deepdiff import DeepDiff


def compare_lists(temp1, temp2, check_key=["completedCount"], all_key=False, num=1):
    """对比两个list中字典，a中字典对应的键值+num等于b字典中键值
    ab值示例：
    a = [{"123": {"a": 1, "b": 2}}, {"456": {"a": 5, "b": 6}}]
    b = [{"123": {"a": 2, "b": 2}}, {"456": {"a": 6, "b": 6}}]
    """
    error = []
    # 同时遍历两个列表中的字典
    for temp1_a, temp2_b in zip(temp1, temp2):
        # 遍历每个字典的键
        for outer_key in temp1_a:
            # 确保 temp2 对应的字典中也有相同的外层键
            if outer_key in temp2_b:
                # 获取内层字典
                inner_dict_a = temp1_a[outer_key]
                inner_dict_b = temp2_b[outer_key]
                # 提取内层字典key并存入list中
                inner_dict_a_keys = list(inner_dict_a)
                if all_key is False:
                    inner_dict_a_keys = check_key
                # 遍历内层字典的键
                for inner_key in inner_dict_a_keys:
                    # 确保 temp2 对应的内层字典中也有相同的键
                    if inner_key in inner_dict_a.keys():
                        # 检查是否满足条件
                        if inner_dict_a[inner_key] + num != inner_dict_b[inner_key]:
                            error.append({
                                outer_key: {
                                    f"{inner_key}_in_a": inner_dict_a[inner_key],
                                    f"{inner_key}_in_b": inner_dict_b[inner_key]
                                }
                            })
    return error


def contrast_dict(actual_dict, expected_dict, **kwargs):
    """对比两个字典相同key的值"""
    result = DeepDiff(expected_dict, actual_dict)
    print("字典对比后结果:", result)
    if kwargs.get("only_values_changed", True):
        return [False, result["values_changed"]] \
            if "values_changed" in result.keys() else [True, "校验正常"]
    else:
        return [True, "校验正常"] if not result else [False, result]


def json_to_dict(json_data=None):
    if json_data is None:
        with open("/Users/SL/project/python/smartpush_autotest/smartpush/test.json", "r", encoding="utf-8") as file:
            json_result = json.load(file)
    return json_result
