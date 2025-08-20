import json
from tenacity import retry, stop_after_attempt, wait_fixed
from smartpush.base.request_base import FormRequestBase
from smartpush.base.url_enum import URL
from smartpush.crowd import crowd
from smartpush.export.basic.GetOssUrl import log_attempt


class FormAfter(FormRequestBase):
    def __init__(self, form_id, host, headers):
        super().__init__(form_id, host, headers)

    def callPageFormReportDetail(self, reportDetailType, start_time=None, end_time=None):
        """
        获取PageFormReportDetail数据
        :param end_time:
        :param start_time:
        :param reportDetailType:
        :return:
        """
        requestParam = {"page": 1, "pageSize": 20, "reportDetailType": reportDetailType, "formId": self.form_id}
        if start_time is not None and end_time is not None:
            requestParam["startTime"] = start_time
            requestParam["endTime"] = end_time
        result = self.request(method=URL.pageFormReportDetail.method, path=URL.pageFormReportDetail.url,
                              data=requestParam)
        persons_list = result["resultData"]["reportDetailData"]["datas"]
        return persons_list

    def callGetFormReportDetail(self):
        requestParam = {"formId": self.form_id}
        result = self.request(method=URL.getFormReportDetail.method, path=URL.getFormReportDetail.url,
                              data=requestParam)
        resultData = result["resultData"]
        return resultData

    def callGetFormPerformanceTrend(self):
        requestParam = {"formId": self.form_id}
        result = self.request(method=URL.getFormPerformanceTrend.method, path=URL.getFormPerformanceTrend.url,
                              data=requestParam)
        resultData = result["resultData"]
        return resultData

    def callGetFormList(self, formName):
        requestParam = {'page': 1, 'pageSize': 10, 'name': formName}
        result = self.request(method=URL.getFormList.method, path=URL.getFormList.url, data=requestParam)
        return result["resultData"]['datas']

    def callGetFormInfo(self):
        requestParam = {'formId': self.form_id}
        result = self.request(method=URL.getFormInfo.method, path=URL.getFormInfo.url, params=requestParam)
        return result['resultData']

    def callDeleteForm(self, merchant_id):
        requestParam = {"formId": self.form_id, "merchant_id": merchant_id}
        result = self.request(method=URL.deleteForm.method, path=URL.deleteForm.url, params=requestParam)
        assert result['code'] == 1
        print(f"删除id:{self.form_id}表单成功")

    # --------        处理数据  --------------
    def collectFormDetails(self, key, start_time=None, end_time=None):
        """
        从表单收集明细中获取信息，判断是否收集成功
        :param self:
        :param key: 关键词
        :param start_time: 开始时间
        :param end_time: 结束时间
        """
        persons_list = self.callPageFormReportDetail("FORM_COLLECT", start_time, end_time)
        if persons_list:
            for person in persons_list:
                if person['email'] == key:
                    return True, person
                elif person['phone'] == key:
                    return True, person
                else:
                    return False, None

    def FormReportNumQuery(self, num_type="viewNum", assertNum=None):
        """
        表单数据数据统计
        :param assertNum:
        :param num_type:viewNum/clickNum/collectNum/orderNum
        """
        data = self.callGetFormReportDetail()
        if data is not None:
            if assertNum is None:
                var = data.get(num_type)
                return var
            else:
                return data.get(num_type) == assertNum

    def getFormAttributionSales(self, key, start_time=None, end_time=None):
        """
        判断折扣码是否能正确归因
        :param key:
        :param start_time:
        :param end_time:
        :return:
        """
        order_list = self.callPageFormReportDetail("FORM_SALES", start_time, end_time)
        if order_list:
            for order in order_list:
                if order['email'] == key:
                    return True, order
                elif order['phone'] == key:
                    return True, order
                elif order['orderId'] == key:
                    return True, order
                else:
                    return False, None

    def getFormLineChart(self, date=None, num_type="viewNum", assertNum=None):
        """
        获取表单折线图
        :param assertNum:
        :param date:
        :param num_type:viewNum/clickNum/collectNum
        """
        datas = dict(self.callGetFormPerformanceTrend())
        if datas is not None:
            for data in datas:
                if data.get(date):
                    if assertNum is not None:
                        assert data.get(num_type) == assertNum
                    else:
                        return data.get(num_type)

    def getCrowdPersonList(self, _id, page=1, pageSize=20, filter_type="email", filter_value=""):
        self.callCrowdPersonList(self, _id, page, pageSize, filter_type, filter_value)


if __name__ == '__main__':
    heard = {
        'cookie': 'osudb_appid=SMARTPUSH;osudb_oar=#01#SID0000130BNXOsK5n5eE9jRh/qvw4GkPUL+3WXTwjU1L8VyW4x8OsSN2Z2/Dt4aoaLuvY8+7q9DWFuwOYuZEvYlUl28lCuZSliDRKgR25jsvr/a7AhjqltByzrs9QzPyaHJwgI1LND0Xt4QVU2c5FxQlCfex5;osudb_subappid=1;osudb_uid=4213785247;ecom_http_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTI2Mzg0NzUsImp0aSI6IjU3OTVkMTJkLTFkMDktNGRlZi1hOTFlLWVkNzVlYzRiYzk5YSIsInVzZXJJbmZvIjp7ImlkIjowLCJ1c2VySWQiOiI0MjEzNzg1MjQ3IiwidXNlcm5hbWUiOiIiLCJlbWFpbCI6ImZlbGl4LnNoYW9Ac2hvcGxpbmVhcHAuY29tIiwidXNlclJvbGUiOiJvd25lciIsInBsYXRmb3JtVHlwZSI6Nywic3ViUGxhdGZvcm0iOjEsInBob25lIjoiIiwibGFuZ3VhZ2UiOiJ6aC1oYW5zLWNuIiwiYXV0aFR5cGUiOiIiLCJhdHRyaWJ1dGVzIjp7ImNvdW50cnlDb2RlIjoiQ04iLCJjdXJyZW5jeSI6IkpQWSIsImN1cnJlbmN5U3ltYm9sIjoiSlDCpSIsImRvbWFpbiI6InNtYXJ0cHVzaDQubXlzaG9wbGluZXN0Zy5jb20iLCJsYW5ndWFnZSI6ImVuIiwibWVyY2hhbnRFbWFpbCI6ImZlbGl4LnNoYW9Ac2hvcGxpbmUuY29tIiwibWVyY2hhbnROYW1lIjoiU21hcnRQdXNoNF9lYzJf6Ieq5Yqo5YyW5bqX6ZO6IiwicGhvbmUiOiIiLCJzY29wZUNoYW5nZWQiOmZhbHNlLCJzdGFmZkxhbmd1YWdlIjoiemgtaGFucy1jbiIsInN0YXR1cyI6MCwidGltZXpvbmUiOiJBc2lhL01hY2FvIn0sInN0b3JlSWQiOiIxNjQ0Mzk1OTIwNDQ0IiwiaGFuZGxlIjoic21hcnRwdXNoNCIsImVudiI6IkNOIiwic3RlIjoiIiwidmVyaWZ5IjoiIn0sImxvZ2luVGltZSI6MTc1MDA0NjQ3NTkzNywic2NvcGUiOlsiZW1haWwtbWFya2V0IiwiY29va2llIiwic2wtZWNvbS1lbWFpbC1tYXJrZXQtbmV3LXRlc3QiLCJlbWFpbC1tYXJrZXQtbmV3LWRldi1mcyIsImFwaS11Yy1lYzIiLCJhcGktc3UtZWMyIiwiYXBpLWVtLWVjMiIsImZsb3ctcGx1Z2luIiwiYXBpLXNwLW1hcmtldC1lYzIiXSwiY2xpZW50X2lkIjoiZW1haWwtbWFya2V0In0.T9u3uzrxEulBSMWB-mqkyxEsu6tB-7FVqt9nBhkxPAo;',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTI2Mzg0NzUsImp0aSI6IjU3OTVkMTJkLTFkMDktNGRlZi1hOTFlLWVkNzVlYzRiYzk5YSIsInVzZXJJbmZvIjp7ImlkIjowLCJ1c2VySWQiOiI0MjEzNzg1MjQ3IiwidXNlcm5hbWUiOiIiLCJlbWFpbCI6ImZlbGl4LnNoYW9Ac2hvcGxpbmVhcHAuY29tIiwidXNlclJvbGUiOiJvd25lciIsInBsYXRmb3JtVHlwZSI6Nywic3ViUGxhdGZvcm0iOjEsInBob25lIjoiIiwibGFuZ3VhZ2UiOiJ6aC1oYW5zLWNuIiwiYXV0aFR5cGUiOiIiLCJhdHRyaWJ1dGVzIjp7ImNvdW50cnlDb2RlIjoiQ04iLCJjdXJyZW5jeSI6IkpQWSIsImN1cnJlbmN5U3ltYm9sIjoiSlDCpSIsImRvbWFpbiI6InNtYXJ0cHVzaDQubXlzaG9wbGluZXN0Zy5jb20iLCJsYW5ndWFnZSI6ImVuIiwibWVyY2hhbnRFbWFpbCI6ImZlbGl4LnNoYW9Ac2hvcGxpbmUuY29tIiwibWVyY2hhbnROYW1lIjoiU21hcnRQdXNoNF9lYzJf6Ieq5Yqo5YyW5bqX6ZO6IiwicGhvbmUiOiIiLCJzY29wZUNoYW5nZWQiOmZhbHNlLCJzdGFmZkxhbmd1YWdlIjoiemgtaGFucy1jbiIsInN0YXR1cyI6MCwidGltZXpvbmUiOiJBc2lhL01hY2FvIn0sInN0b3JlSWQiOiIxNjQ0Mzk1OTIwNDQ0IiwiaGFuZGxlIjoic21hcnRwdXNoNCIsImVudiI6IkNOIiwic3RlIjoiIiwidmVyaWZ5IjoiIn0sImxvZ2luVGltZSI6MTc1MDA0NjQ3NTkzNywic2NvcGUiOlsiZW1haWwtbWFya2V0IiwiY29va2llIiwic2wtZWNvbS1lbWFpbC1tYXJrZXQtbmV3LXRlc3QiLCJlbWFpbC1tYXJrZXQtbmV3LWRldi1mcyIsImFwaS11Yy1lYzIiLCJhcGktc3UtZWMyIiwiYXBpLWVtLWVjMiIsImZsb3ctcGx1Z2luIiwiYXBpLXNwLW1hcmtldC1lYzIiXSwiY2xpZW50X2lkIjoiZW1haWwtbWFya2V0In0.T9u3uzrxEulBSMWB-mqkyxEsu6tB-7FVqt9nBhkxPAo',
        'Content-Type': 'application/json'}
    host = 'https://test.smartpushedm.com/bff/api-em-ec2'
    after = FormAfter(form_id=19238, headers=heard, host=host)
    after.callDeleteForm('1644395920444')
    # print(after.callGetFormInfo())
