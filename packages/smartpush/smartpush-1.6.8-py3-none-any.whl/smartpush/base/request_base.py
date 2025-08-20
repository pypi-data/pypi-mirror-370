import json

import requests
from requests.adapters import HTTPAdapter
from tenacity import stop_after_attempt, wait_fixed, retry
from urllib3 import Retry

from smartpush.export.basic.GetOssUrl import log_attempt


class RequestBase:
    def __init__(self, host, headers, retries=3, **kwargs):
        """

        :param headers: 头，cookie
        :param host: 域名
        """
        self.host = host
        self.headers = headers
        self.headers.update({"Content-Type":"application/json"})

        # 配置重试策略
        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )

        # 创建 Session 并配置适配器
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), after=log_attempt)
    def request(self, method, path, **kwargs):
        url = f"{self.host}{path}"
        print(f"{method} 请求：", url)
        # 统一处理请求参数
        default_kwargs = {
            "timeout": 30,
            "headers": self.headers
        }
        response_json = None
        default_kwargs.update(kwargs)
        if default_kwargs.get('data'):  # 如果data有值json序列化
            data = json.dumps(default_kwargs.get('data'))
            default_kwargs.update({'data': data})
        try:
            response = self.session.request(method, url, **default_kwargs)
            response.raise_for_status()
            response_json = response.json()
            print("响应内容为：\n", json.dumps(response_json,ensure_ascii=False))
            assert response_json['code'] == 1
            return response_json
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None
        except Exception as e:
            raise e


class FormRequestBase(RequestBase):
    def __init__(self, form_id, host, headers, **kwargs):
        super().__init__(host, headers, **kwargs)
        self.form_id = form_id


class CrowdRequestBase(RequestBase):
    def __init__(self, crowd_id, host, headers, **kwargs):
        super().__init__(host, headers, **kwargs)
        self.crowd_id = crowd_id
