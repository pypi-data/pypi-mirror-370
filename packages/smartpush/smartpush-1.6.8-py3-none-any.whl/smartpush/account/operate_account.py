import json
import requests


def del_merchant_sub_account(cookies, ac_host, merchantId, platform, num=None):
    """删除店铺未验证子账号"""
    if num is None or num == "":
        num = 49
        # 查询店铺所有子账号
    role_url = ac_host + "/role/getMerchantRoles"
    role_headers = {
        'cookie': cookies
    }
    params = {"merchantId": merchantId, "plat": platform}
    del_roles = {}
    role_result = json.loads(requests.request("GET", url=role_url, params=params, headers=role_headers).text)
    if num > len(role_result["resultData"]["merchantRoleInfos"]):
        num = len(role_result["resultData"]["merchantRoleInfos"])
    for i in range(num):
        if not (role_result["resultData"]["merchantRoleInfos"][i]["status"] == "1" or
                role_result["resultData"]["merchantRoleInfos"][i]["role"] == "owner"):
            del_roles[i] = role_result["resultData"]["merchantRoleInfos"][i]
            del_roles[i]["plat"] = role_result["resultData"]["plat"]
            del_roles[i]["merchantId"] = merchantId
            del del_roles[i]["status"]
            del del_roles[i]["name"]

    # 删除子账号
    del_role_url = ac_host + "/role/delMerchantRole"
    role_headers["content-type"] = 'application/json'
    results = []
    for i in del_roles.values():
        del_role_result = requests.request("POST", url=del_role_url, headers=role_headers, data=json.dumps(i)).text
        results.append({i["email"]: del_role_result})

    print(f"已删除账号: {results}")
