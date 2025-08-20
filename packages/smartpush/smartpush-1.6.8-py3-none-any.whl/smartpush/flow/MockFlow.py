import json
import random
import time
import requests
from smartpush.flow import global_flow
from smartpush.utils import ListDictUtils


def get_current_flow(host_domain, cookies, flow_id, splits=None, **kwargs):
    """# 提取flow所有节点数据
    splits: list, 需断言时填写, 拆分节点走向,必须走到终点, 如: ["false", "true"]，即走到拆分节点限制不满足分支再走满足分支
    get_email_content: bool，是否提取邮件内容
    """
    _url = host_domain + "/flow/getFlowDetail"
    headers = {
        "cookie": cookies
    }
    params = {
        "flowId": flow_id,
        "active": True,
        "includeActivityDetail": True
    }
    result = json.loads(requests.request(method="get", url=_url, headers=headers, params=params).text)
    # 按节点id存储
    node_counts = []
    get_email_content = kwargs.get("get_email_content", False)
    email_contents = []

    def process_node(node, split_num=0, index_type="completedCount"):
        # 如当前分支为拆分节点，根据走yes还是no分支取对应字段
        if "split" == node["type"] and splits is not None and len(splits) > split_num:
            index_type = "completedCount" if splits[split_num] == "true" else "skippedCount"
        node_counts.append({node["id"]: {index_type: node["data"][index_type]
                                         }
                            })
        # 提取邮件内容
        if get_email_content and node["type"] == "sendLetter":
            email_contents.append({node["data"]["sendLetter"]["emailName"]: {
                "receiveAddress": node["data"]["sendLetter"]["receiveAddress"],
                "sender": node["data"]["sendLetter"]["sender"],
            }})
        # 处理split节点
        if "split" == node["type"] and splits is not None and len(splits) > split_num:
            split_branch = node['data']['split']['branches'][splits[split_num]]
            split_num += 1
            for branch_node in split_branch:
                process_node(branch_node, split_num)
        # # 处理abTesting节点
        # elif "abTesting" in node["data"].keys():
        #     for branch_node in node['data']['abTesting']['branches']["a"]:
        #         process_node(branch_node)
        #     for branch_node in node['data']['abTesting']['branches']["b"]:
        #         process_node(branch_node)

    # 处理所有顶层节点
    for node in result['resultData']['nodes']:
        process_node(node=node)
    return node_counts, result["resultData"]["version"], email_contents if get_email_content else None


def mock_pulsar(mock_domain, pulsar, limit=1):
    """
    # post请求
    # times：为触发次数，默认1次即可
    """
    _url = mock_domain + "/flow/testEventMulti"
    headers = {
        "Content-Type": "application/json"
    }
    # 生成随机message_id
    prefix = 179
    pulsar["messageId"] = f"{prefix}{random.randint(10 ** 15, 10 ** 16 - 1)}"
    params = {
        "times": limit,
        "mq": pulsar
    }
    print(params)
    result = requests.request(method="post", url=_url, headers=headers, json=params).text
    return json.loads(result)


def check_flow(host_domain, cookies, mock_domain="", **kwargs):
    """
    完整触发流程
    params
    mock_domain:必填，触发接口域名
    host_domain:必填，spflow接口域名
    cookies:必填，sp登录态
    flow_id:必填
    pulsar:必填，模拟的触发数据
    split_steps: 默认为all，需拆分步骤时填写，枚举：all、one、two；
        one:获取旧节点数据和触发；
        two：获取触发后数据和断言节点数据

    old_flow_counts: 拆分两步时步骤二必填，内容为步骤一的返回值
    limit:非必填，默认为1 - mock_pulsar函数用于控制模拟触发的次数
    sleep_time: 非必填, 默认60s, 等待时间，用于触发后等待各节点计数后获取新数据
    update_flow_params: 非必填，dict格式，需更新flow时传参，参数结构为sp的saveFlow接口内容
    num:非必填，默认为1 - compare_lists函数用于断言方法做差值计算
    all_key: 非必填，bool，默认false，输入true时，检查指标节点常用5个字段
    check_key: 非必填, 默认只有completedCount, list格式，传入需检查节点的指标key，如：completedCount、skippedCount、openRate等
    split_node: list，有拆分节点时需填，结构：如: ["false", "true"]，即走到拆分节点限制不满足分支再走满足分支
    get_email_content: bool，默认false, 提取邮件内容，用于断言邮箱内是否送达
    """
    # todo: 还差邮件校验部分，后续补充
    is_split_steps = kwargs.get("split_steps", "all")
    # 步骤1 - 所需字段：split_steps、host_domain、cookies、flow_id、pulsar
    if is_split_steps == "one" or is_split_steps == "all":
        # 触发前提取flow数据，后续做对比
        old_flow_counts, old_versions, _ = get_current_flow(host_domain=host_domain, cookies=cookies,
                                                            flow_id=kwargs["flow_id"],
                                                            splits=kwargs.get("split_node", None))
        kwargs["old_flow_counts"] = old_flow_counts
        # 更新flow
        if kwargs.get("update_flow_params", False):
            global_flow.update_flow(host_domain=host_domain, cookies=cookies,
                                    update_flow_params=kwargs.get("update_flow_params"),
                                    version=old_versions, flow_id=kwargs["flow_id"])
        # 启动flow
        global_flow.start_flow(host_domain=host_domain, cookies=cookies, flow_id=kwargs["flow_id"],
                               version=old_versions)
        # 触发flow
        mock_pulsar(mock_domain=mock_domain, pulsar=kwargs["pulsar"], limit=kwargs.get("limit", 1))
        if is_split_steps == "one":
            return old_flow_counts, old_versions

    # 步骤2
    if is_split_steps == "two" or is_split_steps == "all":
        if is_split_steps == "all":
            time.sleep(kwargs.get("sleep_time", 60))
        # 触发后提取flow数据，做断言
        new_flow_counts, new_versions, email_contents = get_current_flow(host_domain=host_domain, cookies=cookies,
                                                                         flow_id=kwargs["flow_id"],
                                                                         splits=kwargs.get("split_node", None),
                                                                         get_email_content=kwargs.get(
                                                                             "get_email_content", False))
        # 断言
        result = ListDictUtils.compare_lists(temp1=kwargs.get("old_flow_counts"),
                                             temp2=new_flow_counts, num=kwargs.get("num", 1),
                                             check_key=kwargs.get("check_key", ["completedCount", "skippedCount"]),
                                             all_key=kwargs.get("all_key", False))
        return [True, "断言成功"] if len(result) == 0 else [False, result], email_contents
