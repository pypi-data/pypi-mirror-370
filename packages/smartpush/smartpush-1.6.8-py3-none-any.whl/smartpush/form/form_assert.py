"""
获取在线有效表单列表，并判断是否触发对应的表单
"""
from smartpush.base.request_base import FormRequestBase


class FormAssert(FormRequestBase):

    def getValidForms(self):
        self.post()



"""
C端与B端数据比较
"""

