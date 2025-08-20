import copy
import json
from urllib.parse import unquote
from smartpush.export.basic.ReadExcel import *
from datetime import datetime
from smartpush.utils import DataTypeUtils

"""
用于excel校验
"""
warnings.simplefilter("ignore")


def check_excel(check_type="content", **kwargs):
    """对比excel
    :param: type: 需要对比类型，
            枚举：content：对比两表格内容
                方式1：传参actual_oss和expected_oss，参数类型str,url
                放松1：传参actual和expected，参数类型list or dict
            excelName: 对比两表格文件名称
            all: 对比所有内容
    """
    try:
        if "type" not in kwargs.keys():
            kwargs["type"] = ".xlsx"
        if check_type == "content":
            if "actual" in kwargs.keys() and "expected" in kwargs.keys():
                return check_excel_content(actual=kwargs["actual"], expected=kwargs["expected"])
            else:
                return check_excel_content(
                    actual=read_excel_and_write_to_list(excel_data=read_excel_from_oss(url=kwargs["actual_oss"]),
                                                        **kwargs),
                    expected=read_excel_and_write_to_list(excel_data=read_excel_from_oss(url=kwargs["expected_oss"]),
                                                          **kwargs)
                )
        elif check_type == "excelName":
            return check_excel_name(actual_oss=kwargs["actual_oss"], expected_oss=kwargs["expected_oss"])
        elif check_type == "all":
            actual_content = read_excel_and_write_to_list(excel_data=read_excel_from_oss(url=kwargs["actual_oss"]),
                                                          **kwargs)
            expected_content = read_excel_and_write_to_list(excel_data=read_excel_from_oss(url=kwargs["expected_oss"]),
                                                            **kwargs)
            flag1, content_result = check_excel_content(actual=actual_content, expected=expected_content)
            flag2, name_result = check_excel_name(actual_oss=kwargs["actual_oss"], expected_oss=kwargs["expected_oss"])
            return all([flag1, flag2]), {"文件名称": name_result, "导出内容和表头": content_result}
        else:
            return False, f"不支持此类型: {check_type}"
    except Exception as e:
        print(f"对比excel异常：{e}")
        return False, [e]


# # 定义比较类型和对应处理函数的映射
# comparison_functions = {
#     # 内容
#     "content": lambda kwargs: check_excel_content(kwargs["actual"], kwargs["expected"]),
#     # excelName
#     "excelName": lambda kwargs: check_excel_name(kwargs["actual_oss"], kwargs["expected_oss"]),
#     'header': lambda kwargs: check_excel_header(kwargs["actual"], kwargs["expected"]),
#     # 全部
#     "all": lambda kwargs: check_excel_all(kwargs["actual_oss"], kwargs["expected_oss"])
# }
#
#
# def check_excel_for_lu(check_type="content", **kwargs):
#     """对比excel
#     :param: type: 需要对比类型，
#             枚举：
#             content：对比两表格内容
#                 方式1：传参actual_oss和expected_oss，参数类型str,url
#                 放松1：传参actual和expected，参数类型list or dict
#             excelName: 对比两表格文件名称，传oss链接
#             all: 对比所有内容，传oss链接
#     """
#     try:
#         # 根据 check_type 获取对应的处理函数
#         compare_func = comparison_functions.get(check_type)
#         if compare_func:
#             return compare_func(kwargs)
#         else:
#             return False, f"不支持此类型: {check_type}"
#     except KeyError as ke:
#         # raise ke
#         print(f"类型对应参数缺失异常：{ke}")
#         return False, [str(ke)]
#     except Exception as e:
#         print(f"对比 Excel 异常：{e}")
#         return False, [str(e)]


def check_excel_content_form_dict(actual, expected, **kwargs):
    """
    通过 OSS URL 比较 Excel 内容,支持多sheet并且包含表头
    """
    actual, expected = read_excel_and_write_to_dict(actual, **kwargs), read_excel_and_write_to_dict(
        expected, **kwargs)
    return check_excel_content(actual, expected)


def check_excel_content_including_expected(actual, expected, expected_oss, **kwargs):
    """
    通过 OSS URL 比较 Excel 内容,期望是包含的结果,actual传的是生成的oss
    """
    actual, expected = read_excel_and_write_to_dict(actual, **kwargs), read_excel_and_write_to_dict(
        expected, **kwargs)
    # 判断是否存在差异
    if kwargs.get("export_type") == "flow":
        missing_items = assert_flow(expected, actual, expected_oss)
    else:
        missing_items = find_missing_elements(expected.values(), actual.values())
    return (False, {"与期望结果存在差异": missing_items}) if missing_items else (True, "校验期望结果包含校验通过")


def find_missing_elements(dict1, dict2):
    missing = []
    for element in dict1:
        if element not in dict2:
            missing.append(element)
    return missing


def assert_flow(expected, actual, expected_oss):
    # 判断预期数据in实际导出的数据
    ex_sheet0 = expected.get("sheet0", [])
    ac_sheet0 = actual.get("sheet0", [])
    ex_sheet1 = expected.get("Flow node data by sending time", [])
    ac_sheet1 = actual.get("Flow node data by sending time", [])
    differences = []
    res = []
    ex_sheet1.append(ex_sheet0)
    ac_sheet1.append(ac_sheet0)
    for i in ac_sheet1:
        if i not in ex_sheet1:
            differences.append(i)
            # 判断对应的列数据
            for diff in differences:
                if len(diff) != 24:
                    res.append("列预期不正确")
    # 判断多出的行，获取今天的日期,与预期日期对比
    ex_data = expected_oss.split("/")[4].split("-")
    today = datetime.today()
    target_date = datetime(int(ex_data[0]), int(ex_data[1]), int(ex_data[2]))
    diff_days = (today - target_date).days
    if len(differences) != diff_days:
        res.append("日期预期不正确")
    return res


def check_excel_content_form_list(actual, expected):
    """
    通过 内容 比较 Excel 内容,不包含表头
    """
    expected, actual = read_excel_and_write_to_list(actual), read_excel_and_write_to_list(expected)
    return check_excel_content(actual=actual, expected=expected)


def check_excel_all(actual_oss, expected_oss, check_type=None, **kwargs):
    """
    校验所有内容
    **kwargs: skiprows->int 用于跳过读取行数，如果第一行是动态变化的，建议单独过滤,第一行传1
    """
    file_type = check_and_get_file_suffix_name(actual_oss, expected_oss)
    actual, expected = read_excel_from_oss(actual_oss), read_excel_from_oss(expected_oss)
    actual_data_copy = copy.deepcopy(actual)
    expected_data_copy = copy.deepcopy(expected)
    if kwargs.get("no_check_name", True):
        flag1, name_result = check_excel_name(actual_oss, expected_oss)
        print("校验文件名称")
    else:
        flag1, name_result = True, "不校验文件名称"
        print("不校验文件名称")

    flag3, header_result = check_excel_header(actual_data_copy, expected_data_copy, type=file_type, **kwargs)
    if check_type == "including":
        flag2, content_result = check_excel_content_including_expected(actual, expected, expected_oss, type=file_type,
                                                                       **kwargs)
    else:
        flag2, content_result = check_excel_content_form_dict(actual, expected, type=file_type, **kwargs)
    print(json.dumps(
        {f"文件名称-{flag1}": name_result, f"导出内容-{flag2}": content_result, f"表头校验-{flag3}": header_result},
        ensure_ascii=False))
    return all([flag1, flag2, flag3])


def check_and_get_file_suffix_name(actual_oss, expected_oss, **kwargs) -> str:
    """
    校验并获取oss的后缀类型
    @param actual_oss:
    @param expected_oss:
    @return:
    """
    actual_file_suffix_name = get_file_suffix_name(actual_oss)
    expected_file_suffix_name = get_file_suffix_name(expected_oss)
    if actual_oss == expected_oss and kwargs.get("test", False):
        raise Exception("oss链接不允许相同，请检查oss链接是否为相同链接,调试需要请传参数test=True")
    try:
        assert actual_file_suffix_name == expected_file_suffix_name
        return actual_file_suffix_name
    except Exception:
        raise Exception("oss文件类型不一致,请检查oss链接是否为相同类型")


def check_excel_name(actual_oss, expected_oss):
    """校验excel文件名称
    :param actual_oss:实际oss链接
    :param actual_oss:预期oss链接
    """
    try:
        actual_name = unquote(actual_oss.split("/")[-1])
        expected_name = unquote(expected_oss.split("/")[-1])
        if actual_name == expected_name:
            return True, "excel文件名称-完成匹配"
        else:
            return False, f"excel文件名称-不匹配, 实际: {actual_name}, 预期: {expected_name}"
    except BaseException as msg:
        return False, f"excel文件名称-服务异常: {msg}"


def check_excel_content(actual, expected):
    """校验excel内容
       :param actual: 实际内容，list或dict类型
       :param expected:预期内容：list或dict类型
     """
    try:
        if actual == expected:
            return True, ["excel内容和表头-完全匹配"]
        else:
            errors = []
            # 断言1：对比sheet数
            errors = []
            actual_num, expected_num = len(actual), len(expected)
            errors.append("预期和实际sheet数相等，为" + str(
                actual_num) + "个" if actual_num - expected_num == 0 else "sheet数和预期对比差" + str(
                actual_num - expected_num) + "个" + ", 实际:" + str(actual_num) + " 预期: " + str(expected_num))
            # 断言2：对比具体行
            if isinstance(actual, list) and isinstance(expected, list):
                # 第一层提取sheet
                for i in range(max(len(expected), len(actual))):
                    if len(expected) <= i:
                        errors.append(f"预期结果不存在第{i + 1}个sheet")
                        continue
                    elif len(actual) <= i:
                        errors.append(f"预期结果不存在第{i + 1}个sheet")
                        continue
                    else:
                        if actual[i] == expected[i]:
                            continue
                        else:
                            for row in range(max(len(expected[i]), len(actual[i]))):
                                if len(expected[i]) <= row:
                                    errors.append(f"预期结果不存在第{row + 1}个行")
                                    continue
                                elif len(actual[i]) <= row:
                                    errors.append(f"实际内容不存在第{row + 1}个行")
                                    continue
                                else:
                                    if actual[i][row] == expected[i][row]:
                                        continue
                                    else:
                                        errors.append(
                                            f"第{i + 1}个sheet的内容-第" + str(i + 1) + "行不匹配，预期为：" + str(
                                                expected[i]) + ", 实际为: " + str(
                                                actual[i]))
                return False, errors
            else:
                return False, compare_dicts(actual, expected)
    except Exception as e:
        print(f"：excel内容-服务异常{e}")
        return False, [e]


def check_excel_header(actual, expected, **kwargs):
    """
    比较两个文档第一列的header是否一致
    @param actual:
    @param expected:
    @return:
    @return:
    """
    try:
        actual1, expected1 = read_excel_header(actual, return_type='dict', **kwargs), read_excel_header(expected,
                                                                                                        return_type='dict',
                                                                                                        **kwargs)
        try:
            result = check_excel_content(actual1, expected1)
            assert result[0]
            return True, "表头校验值与顺序一致"
        except Exception as e:
            return False, f"表头校验值与顺序失败 {result[1]}"
    except Exception as e:
        return False, f"表头校验异常 {e}"


def check_excel_header_by_list(actual, expected, **kwargs):
    """
    比较导出表头是否一致是否一致
    @param actual: 可以传oss链接
    @param expected:期望的表头list
    @return:
    @return:
    """
    try:
        if not isinstance(actual, io.BytesIO):
            actual = read_excel_from_oss(actual)
        actual1, expected1 = read_excel_header(actual, **kwargs)[0], get_header_map_data(
            expected)
        actual1.sort()
        diff = None
        try:
            diff = compare_lists(actual1, expected1)
            assert not diff  # 为空则错误
            return True
        except AssertionError:
            print("actual:", actual1)
            print("expected:", expected1)
            print(diff)
            return False
    except Exception as e:
        raise e


def get_header_map_data(name_list):
    """
        获取头映射关系--中文
        :param name_list:
        :return:
        """
    header_dict_zh_cn = {
        "sendTypeName": "活动类型",
        "activityName": "活动名称",
        "sendTotal": "发送数",
        "deliveryTotal": "送达数", # 原本是送达人数
        # "deliveryRate": "送达率",
        "openRate": ["打开率（打开数/送达数）", "打开数"],
        # "openRate": "打开率（打开数/送达数）",
        "noRepeatOpenRate": ["不重复打开率", "不重复打开"],
        # "noRepeatOpenRate": "不重复打开率",
        "clickRate": ["点击率（点击数/送达数）", "点击数"],
        # "clickRate": "点击率（点击数/送达数）",
        "noRepeatClickRate": ["不重复点击率", "不重复点击"],
        # "noRepeatClickRate": "不重复点击率",
        "salesPriceTotal": "销售额",
        "orderTotal": "订单数",
        "averageOrderValue": "平均订单价值",
        "conversionRate": "转化率",
        "unsubTotal": "退订数",
        "unsubRate": "退订率",
        "complainRate": "投诉率",
        "bounceRate": "弹回邮箱率",
        "sendStartTime": "发送时间"
    }
    header_list = []
    for key, value in header_dict_zh_cn.items():
        if key in name_list:
            header_list.append(value) if not isinstance(value, list) else header_list.extend(value)
    header_list.sort()
    return header_list


def del_temp_file(file_name=""):
    """删除temp下临时文件"""
    file_path = os.path.join(os.path.dirname(os.getcwd()) + "/temp_file/" + file_name)
    try:
        os.remove(file_path)
        print(f"文件 {file_path} 已成功删除。")
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在。")
    except Exception as e:
        print(f"删除文件 {file_path} 时出错：{e}")


def compare_dicts(actual_dict, expected_dict):
    diff = {}
    # 找出只在 dict1 中存在的键
    only_in_dict1 = set(actual_dict.keys()) - set(expected_dict.keys())
    if only_in_dict1:
        diff['only_in_dict1'] = {key: actual_dict[key] for key in only_in_dict1}
    # 找出只在 dict2 中存在的键
    only_in_dict2 = set(expected_dict.keys()) - set(actual_dict.keys())
    if only_in_dict2:
        diff['only_in_dict2'] = {key: expected_dict[key] for key in only_in_dict2}
    # 处理两个字典都有的键
    common_keys = set(actual_dict.keys()) & set(expected_dict.keys())
    for key in common_keys:
        value1 = actual_dict[key]
        value2 = expected_dict[key]
        if isinstance(value1, dict) and isinstance(value2, dict):
            # 如果值是字典，递归比较
            sub_diff = compare_dicts(value1, value2)
            if sub_diff:
                diff[f'不同的字典_at_{key}'] = sub_diff
        elif isinstance(value1, list) and isinstance(value2, list):
            # 如果值是列表，递归比较列表元素
            list_diff = compare_lists(value1, value2)
            if list_diff:
                diff[f'sheet【{key}】中存在差异'] = list_diff
        else:
            # 其他情况，直接比较值
            if value1 != value2:
                diff[f'不同的值_at_{key}'] = (value1, value2)
    return diff


def compare_lists(actual_dict_list, expected_dict_list):
    diff = []
    max_len = max(len(actual_dict_list), len(expected_dict_list))
    for i in range(max_len):
        if i >= len(actual_dict_list):
            # list2 更长
            diff.append(('只存在expected_dict_list的中', expected_dict_list[i]))
        elif i >= len(expected_dict_list):
            # list1 更长
            diff.append(('只存在actual_dict_list中', actual_dict_list[i]))
        else:
            item1 = actual_dict_list[i]
            item2 = expected_dict_list[i]
            if isinstance(item1, dict) and isinstance(item2, dict):
                # 如果元素是字典，递归比较
                sub_diff = compare_dicts(item1, item2)
                if sub_diff:
                    diff.append(('列表索引中存在不同的字典', i, sub_diff))
            elif isinstance(item1, list) and isinstance(item2, list):
                # 如果元素是列表，递归比较
                sub_list_diff = compare_lists(item1, item2)
                if sub_list_diff:
                    diff.append(('列表索引的存在不同的子列表', i, sub_list_diff))
            else:
                if item1 != item2:
                    diff.append(('列表索引的不同值', i, (item1, item2)))
    return diff


def check_field_format(actual_oss, **kwargs):
    """
        逐个校验字段类型
        **kwargs: fileds为需检查字段，结构为dict，如{0: {0: "email", 1: "time"}},
        即校验第一个sheet第二个字段需符合email格式，第二个字段需符合time格式
        """
    # 获取oss内容并存入dict
    actual = read_excel_from_oss(actual_oss)
    actual_dict = read_excel_and_write_to_dict(actual, **kwargs)
    # 解析参数并校验字段类型
    errors = []
    actual_dict_key = list(actual_dict.keys())
    for key in kwargs["fileds"].keys():
        if isinstance(key, int) and 0 <= key < len(actual_dict):
            for filed_key in kwargs["fileds"][key].keys():
                num = 1
                for row in actual_dict[actual_dict_key[key]]:
                    if kwargs["fileds"][key][filed_key] == "email":
                        fool = DataTypeUtils.DataTypeUtils().check_email_format(email=row[filed_key])
                        if not fool:
                            errors.append(
                                f"{actual_dict_key[key]} 表, 第{num}行{filed_key}列{kwargs['fileds'][key][filed_key]}格式不符合规范, 值为:{row[filed_key]}")
                    elif kwargs["fileds"][key][filed_key] == "time":
                        fool = DataTypeUtils.DataTypeUtils().check_time_format(time_str=row[filed_key],
                                                                               precision=kwargs.get('precision', 's'))
                        if not fool:
                            errors.append(
                                f"{actual_dict_key[key]} 表, 第{num}行{filed_key}列{kwargs['fileds'][key][filed_key]}格式不符合规范, 值为:{row[filed_key]}")
                    num += 1
    print(errors if len(errors) > 0 else "都校验成功")
    return False if len(errors) > 0 else True
