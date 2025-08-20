import json
import urllib

import requests
from requests import HTTPError
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError, stop_any
from smartpush.utils.StringUtils import StringUtils

export_requestParam = {
    "page": 1,
    "pageSize": 20,
    "type": "EXPORT",
    "status": None,
    "startTime": None,
    "endTime": None
}

import_requestParam = {
    "page": 1,
    "pageSize": 20,
    "type": "IMPORT",
    "status": None,
    "startTime": None,
    "endTime": None
}

manually_stop = False  # 手动停止表示


# 用于技术第几次重试，无需修改
def log_attempt(retry_state):
    """
    回调函数，在每次重试时记录并打印重试次数
    """
    attempt_number = retry_state.attempt_number
    print(f"当前重试次数: {attempt_number}")


# 自定义停止条件函数
def should_stop(retry_state):
    if manually_stop:
        print("数据导入/导出状态是失败，立即停止重试")
    return manually_stop


def get_oss_address_with_retry(target_id, url, requestHeader, requestParam=None, is_import=False, **kwargs) -> str:
    """
    创建带有动态重试配置的获取 OSS 地址
    **kwargs 可传参：tries=10, delay=2, backoff=1
    :param is_import: 如果是导入的则传True
    :param requestParam:
    :param url:
    :param target_id:
    :param requestHeader:
    :return: 带有重试配置的获取 OSS 地址的
    """
    if requestParam is None:
        requestParam = import_requestParam if is_import else export_requestParam
    tries = kwargs.get('tries', 30)  # 重试次数
    delay = kwargs.get('delay', 2)
    _url = url + '/bulkOps/query'
    if StringUtils.is_empty(target_id):
        raise ValueError("缺少target_id参数")

    def bulkOps_query(_url, _requestHeader, _requestParam):
        response = requests.request(url=_url, headers=_requestHeader, data=json.dumps(_requestParam),
                                    method="post")
        response.raise_for_status()
        result = response.json()
        if result['code'] != 1:
            raise HTTPError(f"{result}")
        return result

    @retry(stop=stop_after_attempt(tries) | stop_any(should_stop), wait=wait_fixed(delay), after=log_attempt)
    def get_oss_address():
        try:
            result = bulkOps_query(_url, requestHeader, requestParam)
            id_url_dict = {item["id"]: item["url"] for item in result["resultData"]["datas"]}
            id_status_dict = {item["id"]: [item["status"], item["reason"]] for item in result["resultData"]["datas"]}
            if target_id in id_url_dict:
                if id_status_dict[target_id][0] == "FAIL":
                    reason = id_status_dict[target_id][1]
                    print(f"导出id {target_id}失败，原因是 [{reason}]")
                    global manually_stop
                    manually_stop = True
                if len(id_url_dict[target_id]) == 1:
                    target_url = urllib.parse.unquote(id_url_dict[target_id][0])
                    print(f"target_id [{target_id}] 的oss链接为： {target_url}")
                    return target_url
                else:
                    raise ValueError(f"存在多条 id 为 {target_id} 的记录，记录为：{id_url_dict[target_id]}")
            else:
                raise ValueError(f"未找到 导出id 为 {target_id} 的记录，未包含有效的 OSS 地址")
        except (KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"响应数据格式错误,响应结果: {result},异常: {e}")
        except requests.RequestException as e:
            print(f"请求发生异常: {e}，正在重试...")
            raise

    @retry(stop=stop_after_attempt(tries) | stop_any(should_stop), wait=wait_fixed(delay), after=log_attempt)
    def get_import_success():
        target_id_list = []
        try:
            result = bulkOps_query(_url, requestHeader, requestParam)
            for item in result["resultData"]["datas"]:
                if item.get("id") == int(target_id):
                    status = item.get("status")
                    reason = item.get("reason")
                    if status == "FAIL":
                        print(f"导入id {target_id}失败，原因是 [{reason}]")
                        global manually_stop
                        manually_stop = True
                    assert status == "SUCCESS"
                    return f"导入id {target_id} 导入成功"
                else:
                    target_id_list.append(item.get("id"))
            if target_id not in target_id_list:
                raise ValueError(f"未找到 导入id 为 {target_id} 的记录，请检查是否发起导入")
        except AssertionError:
            raise AssertionError(f"导入id 为 {target_id} 的记录非SUCCESS，状态为：{status}")
        except (KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"响应数据格式错误,响应结果: {result},异常: {e}")
        except requests.RequestException as e:
            print(f"请求发生异常: {e}，正在重试...")
            raise
        except Exception:
            raise

    def cancel_export_file(_target_id):
        """
        用于失败后取消导出/导入
        :param _target_id:
        :return:
        """
        cancel_url = url + '/bulkOps/cancel'
        response = requests.request(url=cancel_url, headers=requestHeader, params={'id': _target_id}, method="get")
        response.raise_for_status()
        result = response.json()
        if is_import:
            print(f"导入文件失败，取消 {_target_id} 的导入记录，响应：{result}")
        else:
            print(f"获取Oss Url失败，取消 {_target_id} 的导出记录，响应：{result}")
        return result

    try:
        if is_import:
            return get_import_success()
        else:
            return get_oss_address()
    except Exception as e:
        # print(f"最终失败，错误信息: {e}")
        if isinstance(e, RetryError):
            cancel_export_file(target_id)
        return f"执行失败，错误信息: {e}"
