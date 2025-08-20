import json

from smartpush.base.request_base import CrowdRequestBase, RequestBase
from smartpush.base.url_enum import URL
from smartpush.export.basic.ExcelExportChecker import compare_lists, compare_dicts
from smartpush.export.basic.ReadExcel import read_excel_file_form_local_path


class Crowd(CrowdRequestBase):

    def callEditCrowdPackage(self, crowdName="", groupRules=None, groupRelation="$AND",
                             triggerStock=False):
        """
        更新群组条件id
        :param triggerStock:
        :param crowdName:
        :param groupRules:
        :param groupRelation:
        :return:
        """
        requestParam = {"id": self.crowd_id, "crowdName": crowdName, "groupRelation": groupRelation,
                        "groupRules": groupRules, "triggerStock": triggerStock}
        result = self.request(method=URL.editCrowdPackage.method, path=URL.editCrowdPackage.url, data=requestParam)
        return result['resultData']

    def callCrowdPersonListInPackage(self, page=1, pageSize=20, filter_type=None, filter_value=None):
        """
        获取群组联系人列表
        :param page:
        :param pageSize:
        :param filter_type:
        :param filter_value:
        :return:
        """
        requestParam = {"id": self.crowd_id, "page": page, "pageSize": pageSize}
        if filter_value is not None:
            requestParam["filter"] = {filter_type: {"in": filter_value}}
        result = self.request(method=URL.crowdPersonListInPackage.method, path=URL.crowdPersonListInPackage.url,
                              data=requestParam)
        resultData = result['resultData']
        return resultData

    def callCrowdPackageDetail(self, page=1, pageSize=20, filter_type=None, filter_value=None):
        """
        获取群组详情
        :param page:
        :param pageSize:
        :param filter_type:
        :param filter_value:
        :return:
        """
        requestParam = {"id": self.crowd_id, "page": page, "pageSize": pageSize, "filter": {}}
        if filter_value is not None:
            requestParam["filter"] = {filter_type: {"in": filter_value}}
        result = self.request(method=URL.crowdPersonList.method, path=URL.crowdPackageDetail.url, data=requestParam)
        resultData = result['resultData']
        return resultData


class CrowdList(RequestBase):
    def callCrowdPackageList(self, page=1, pageSize=20):
        """
        获取群组联系人列表
        :param page:
        :param pageSize:
        :param filter_type:
        :param filter_value:
        :return:
        """
        requestParam = {"page": page, "pageSize": pageSize}
        result = self.request(method=URL.crowdPackageList.method, path=URL.crowdPackageList.url,
                              data=requestParam)
        resultData = result['resultData']
        return resultData


if __name__ == '__main__':
    host = "https://test.smartpushedm.com/bff/api-em-ec2"
    headers = {
        "cookie": "osudb_lang=; a_lang=zh-hans-cn; osudb_appid=SMARTPUSH; osudb_subappid=1; osudb_uid=4600602538; osudb_oar=#01#SID0000133BKWNUKV3dy89d+sUIg8zMRXFm9wRfTTjyv0VTCy96OpvtgkqT1OUFU3CoVCDoViCJBWhmIpO86kPgfbkY9zNHCzZF+4J+Fo1JImvAmc1XF2o9brO79kPj8RrYL1y4u63ddKcJdCIn28V4Uu4k3+g; ecom_http_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTU2NjA0ODgsImp0aSI6IjMxZTFjNGI3LWFkY2YtNDBlNy04MTg5LWExNWI4YmQ4MjdjNCIsInVzZXJJbmZvIjp7ImlkIjowLCJ1c2VySWQiOiI0NjAwNjAyNTM4IiwidXNlcm5hbWUiOiIiLCJlbWFpbCI6Imx1Lmx1QHNob3BsaW5lLmNvbSIsInVzZXJSb2xlIjoib3duZXIiLCJwbGF0Zm9ybVR5cGUiOjcsInN1YlBsYXRmb3JtIjoxLCJwaG9uZSI6IiIsImxhbmd1YWdlIjoiemgtaGFucy1jbiIsImF1dGhUeXBlIjoiIiwiYXR0cmlidXRlcyI6eyJjb3VudHJ5Q29kZSI6IkNOIiwiY3VycmVuY3kiOiJVU0QiLCJjdXJyZW5jeVN5bWJvbCI6IlVTJCIsImRvbWFpbiI6Imx1LWx1LmVtYWlsIiwibGFuZ3VhZ2UiOiJlbiIsIm1lcmNoYW50RW1haWwiOiJsdS5sdUBzaG9wbGluZS5jb20iLCJtZXJjaGFudE5hbWUiOiJsdWx1MzgyLeiuoumYheW8j-eUteWVhiIsInBob25lIjoiIiwic2NvcGVDaGFuZ2VkIjpmYWxzZSwic3RhZmZMYW5ndWFnZSI6InpoLWhhbnMtY24iLCJzdGF0dXMiOjAsInRpbWV6b25lIjoiQXNpYS9TaGFuZ2hhaSJ9LCJzdG9yZUlkIjoiMTc0NTM3NzcwNTkzNiIsImhhbmRsZSI6Imx1bHUzODIiLCJlbnYiOiJDTiIsInN0ZSI6IiIsInZlcmlmeSI6IiJ9LCJsb2dpblRpbWUiOjE3NTMwNjg0ODg4NDQsInNjb3BlIjpbImVtYWlsLW1hcmtldCIsImNvb2tpZSIsInNsLWVjb20tZW1haWwtbWFya2V0LW5ldy10ZXN0IiwiZW1haWwtbWFya2V0LW5ldy1kZXYtZnMiLCJhcGktdWMtZWMyIiwiYXBpLXN1LWVjMiIsImFwaS1lbS1lYzIiLCJmbG93LXBsdWdpbiIsImFwaS1zcC1tYXJrZXQtZWMyIl0sImNsaWVudF9pZCI6ImVtYWlsLW1hcmtldCJ9.mq1cXVbevkTNP6a7kMaU7DAvw18soT0MmZegVf2MH3Y; JSESSIONID=4453B17A35364E6A9D98E6AF1087D50B",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTU2NjA0ODgsImp0aSI6IjMxZTFjNGI3LWFkY2YtNDBlNy04MTg5LWExNWI4YmQ4MjdjNCIsInVzZXJJbmZvIjp7ImlkIjowLCJ1c2VySWQiOiI0NjAwNjAyNTM4IiwidXNlcm5hbWUiOiIiLCJlbWFpbCI6Imx1Lmx1QHNob3BsaW5lLmNvbSIsInVzZXJSb2xlIjoib3duZXIiLCJwbGF0Zm9ybVR5cGUiOjcsInN1YlBsYXRmb3JtIjoxLCJwaG9uZSI6IiIsImxhbmd1YWdlIjoiemgtaGFucy1jbiIsImF1dGhUeXBlIjoiIiwiYXR0cmlidXRlcyI6eyJjb3VudHJ5Q29kZSI6IkNOIiwiY3VycmVuY3kiOiJVU0QiLCJjdXJyZW5jeVN5bWJvbCI6IlVTJCIsImRvbWFpbiI6Imx1LWx1LmVtYWlsIiwibGFuZ3VhZ2UiOiJlbiIsIm1lcmNoYW50RW1haWwiOiJsdS5sdUBzaG9wbGluZS5jb20iLCJtZXJjaGFudE5hbWUiOiJsdWx1MzgyLeiuoumYheW8j-eUteWVhiIsInBob25lIjoiIiwic2NvcGVDaGFuZ2VkIjpmYWxzZSwic3RhZmZMYW5ndWFnZSI6InpoLWhhbnMtY24iLCJzdGF0dXMiOjAsInRpbWV6b25lIjoiQXNpYS9TaGFuZ2hhaSJ9LCJzdG9yZUlkIjoiMTc0NTM3NzcwNTkzNiIsImhhbmRsZSI6Imx1bHUzODIiLCJlbnYiOiJDTiIsInN0ZSI6IiIsInZlcmlmeSI6IiJ9LCJsb2dpblRpbWUiOjE3NTMwNjg0ODg4NDQsInNjb3BlIjpbImVtYWlsLW1hcmtldCIsImNvb2tpZSIsInNsLWVjb20tZW1haWwtbWFya2V0LW5ldy10ZXN0IiwiZW1haWwtbWFya2V0LW5ldy1kZXYtZnMiLCJhcGktdWMtZWMyIiwiYXBpLXN1LWVjMiIsImFwaS1lbS1lYzIiLCJmbG93LXBsdWdpbiIsImFwaS1zcC1tYXJrZXQtZWMyIl0sImNsaWVudF9pZCI6ImVtYWlsLW1hcmtldCJ9.mq1cXVbevkTNP6a7kMaU7DAvw18soT0MmZegVf2MH3Y"}

    crowd_id = "687a028fa34ae35465dc91a2"


    def diff_person(_crowd_id, path):
        ## 这里是查询群组的人的差异
        # list_len = 0
        # flag = True
        # page = 1
        # crowd = Crowd(crowd_id=_crowd_id, host=host, headers=headers)
        # result_list = []
        #
        # while flag:
        #     result = crowd.callCrowdPersonListInPackage(pageSize=100, page=page)
        #     page += 1
        #     num = result['num']
        #     list_len += len(result['responseResult'])
        #     for data in result['responseResult']:
        #         result_list.append(data['id'])
        #     if list_len >= num:
        #         break
        # print(result_list)
        # print("es查询群组数量：", len(result_list))

        # 这里是解析本地文件，查看
        key = ["user_id"]
        data = read_excel_file_form_local_path(path, key)
        print(data)
        print(list(data.get(key)))
        compare_lists(list(data.get("crowd_id")))


    def diff_crowd_num(sql_result_list):
        ## 比较哪些群组数量不一致
        _sql_result_list = {item["crowd_id"]: item["num"] for item in sql_result_list}
        crowd_list = CrowdList(host=host, headers=headers)
        cc = crowd_list.callCrowdPackageList(1, 100)
        crowd_dict = {i['id']: i['nums'] for i in cc['responseList']}

        print("-----sql_result_list-----:\n", json.dumps(sql_result_list, ensure_ascii=False))
        print("****crowd_dict*****:\n", json.dumps(cc, ensure_ascii=False))
        print(f"人群列表数量:{len(crowd_dict)}，hive数量：{len(_sql_result_list)}")
        print(":::::差异:::::\n", json.dumps(compare_dicts(crowd_dict, _sql_result_list), ensure_ascii=False))


    sql_result_list = [
        {
            "crowd_id": "687a0dada34ae35465dc91be",
            "num": "2",
            "version": "1753149225238",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687a028fa34ae35465dc91a2",
            "num": "1110",
            "version": "1753149225238",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "6879fc29a34ae35465dc9198",
            "num": "20",
            "version": "1753149225238",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "6879fc5aa34ae35465dc9199",
            "num": "1084",
            "version": "1753149225238",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "6879f8c6a34ae35465dc9185",
            "num": "9",
            "version": "1753149225237",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "6873eeddf1ac104346194bde",
            "num": "8",
            "version": "1753149225237",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "6877c4aaf40cc91244b1ea05",
            "num": "1097",
            "version": "1753149225237",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "6874b5338c6fe76c51447579",
            "num": "1",
            "version": "1753149225237",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "68778564f40cc91244b1e9fc",
            "num": "42",
            "version": "1753149225237",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "686dea326424e217d9c0c86a",
            "num": "2",
            "version": "1753149225236",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687e171ba5e5180731e2126f",
            "num": "1",
            "version": "1753149225122",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687df922a5e5180731e211d0",
            "num": "4",
            "version": "1753149225120",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687b649aa34ae35465dc934a",
            "num": "2",
            "version": "1753149225119",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687dec0ba5e5180731e2113d",
            "num": "1",
            "version": "1753149225119",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687debd0a5e5180731e2113c",
            "num": "29",
            "version": "1753149225118",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687b632ca34ae35465dc933b",
            "num": "40",
            "version": "1753149225117",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687da2bda34ae35465dc9460",
            "num": "6",
            "version": "1753149225116",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687b3c0ba34ae35465dc9303",
            "num": "38",
            "version": "1753149225116",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687b3670a34ae35465dc92ee",
            "num": "1",
            "version": "1753149225115",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687b38dda34ae35465dc92ef",
            "num": "9",
            "version": "1753149225115",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687b0207a34ae35465dc92da",
            "num": "1",
            "version": "1753149225114",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687b0269a34ae35465dc92db",
            "num": "3",
            "version": "1753149225114",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687afff5a34ae35465dc92d7",
            "num": "2",
            "version": "1753149225113",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687a193aa34ae35465dc91fc",
            "num": "2",
            "version": "1753149225111",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687a1913a34ae35465dc91fb",
            "num": "5",
            "version": "1753149225108",
            "version转日期": "2025-07-22 09:53:45"
        },
        {
            "crowd_id": "687e1908a5e5180731e21272",
            "num": "44",
            "version": "1753149225074",
            "version转日期": "2025-07-22 09:53:45"
        }
    ]
    diff_crowd_num(sql_result_list)

    # diff_person(_crowd_id="687a028fa34ae35465dc91a2",
    #             path="/Users/lulu/Downloads/临时文件2_20250719155155.xls")
