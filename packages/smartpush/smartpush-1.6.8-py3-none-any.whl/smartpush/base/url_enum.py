from enum import Enum, unique


@unique
class URL(Enum):
    """
    :type:表单报告
    """
    pageFormReportDetail = '/formReport/detail/pageFormReportDetail', 'POST'  # 获取表单收集数据
    getFormReportDetail = '/formReport/getFormReportDetail', 'POST'  # 获取表单报告数据(曝光/点击)
    getFormPerformanceTrend = 'formReport/getFormPerformanceTrend', 'POST'

    """
    :type 群组
    """
    editCrowdPackage = '/crowdPackage/editCrowdPackage', 'POST'
    crowdPersonListInPackage = '/crowdPackage/crowdPersonList', 'POST'
    crowdPackageDetail = '/crowdPackage/detail', 'GET'
    crowdPackageList = '/crowdPackage/list', 'POST'

    """
    :type 表单操作
    """
    deleteForm = '/form/deleteFormInfo', 'GET'
    getFormList = '/form/getFormList', 'POST'
    getFormInfo = '/form/getFormInfo', 'GET'

    @property
    def method(self):
        return self.value[1]

    @property
    def url(self):
        return self.value[0]


if __name__ == '__main__':
    print(URL.pageFormReportDetail.method)
    print(URL.getFormReportDetail.url)
