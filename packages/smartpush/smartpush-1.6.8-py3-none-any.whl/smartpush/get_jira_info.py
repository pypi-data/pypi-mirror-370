import datetime
import json
import requests
from jira import JIRA
from smartpush.utils.StringUtils import StringUtils

test_user = {
    "邵宇飞": "dw_shaoyufei",
    "卢泽彬-Lulu-QA": "dw_luzebin",
    "xiangchen zhong": "dw_zhongxiangchen",
    "周彦龙": "dw_zhouyanlong",
    "梁铭津-bryant": "dw_liangmingjin",
    "高忠明 - gaozhongming": "dw_gaozhongming",
    "jiayong zhang": "dw_zhangjiayong",
    "毕杰芳-Dawn Bi": "dw_bijiefang",
    "李志": "dw_lizhi7",
    "张玉吉-小橙C": "dw_zhangyuji",
    "周艳辉-zhouyanhui-QA": "dw_zhouyanhui",
    "zhaoyi wang": "dw_wangzhaoyi",
    "测试-陈美伶-Zoe": "dw_chenmeiling",
    "黄伟灵": "dw_huangweiling",
    "李豪": "dw_lihao10"
}


def get_last_friday_and_this_thursday():
    """
    获取上个周五和本周四的日期
    :return:
    """
    today = datetime.date.today()
    # 计算今天是星期几，0 表示周一，6 表示周日
    weekday = today.weekday()
    # 计算距离上周五的天数
    days_to_last_friday = (weekday + 3) % 7
    if days_to_last_friday == 0:
        days_to_last_friday = 7
    # 得到上周五的日期
    last_friday = today - datetime.timedelta(days=days_to_last_friday)
    # 得到本周四的日期
    this_thursday = last_friday + datetime.timedelta(days=6)
    return last_friday, this_thursday


def get_update_issues_jql():
    """
    根据上周五到本周四的日期范围生成 JQL 查询语句
    """

    # 获取上周五和本周四的日期
    start_date, end_date = get_last_friday_and_this_thursday()

    # 定义 JQL 模板
    jql_template = f'''
        project = "SSP"
        AND issuetype IN (产品需求, 技术需求)
        AND (("计划上线时间[date]" >= "{{start_date}}"
        AND "计划上线时间[date]" <= "{{end_date}}" AND "调整后上线时间[Date]" is EMPTY AND "调整后计划上线时间[Date]" is EMPTY)
        OR ("实际上线时间[date]" >= "{{start_date}}"
        AND "实际上线时间[date]" <= "{{end_date}}") OR ("调整后上线时间[Date]" >= "{{start_date}}"
        AND "调整后上线时间[Date]" <= "{{end_date}}")) AND status NOT IN(需求废弃,需求挂起,需求暂缓)
        ORDER BY cf[12536] ASC, key ASC, cf[12466] ASC, status DESC, created DESC
        '''
    # 填充模板中的日期
    jql_update = jql_template.format(
        start_date=start_date,
        end_date=end_date,
    )
    print(jql_update)
    return jql_update


class JiraInfo:
    def __init__(self, _jira_user, _api_key):
        self.project_name = None
        self.jira_url = "https://shopline.atlassian.net/"
        # self.project_key = _project_key
        self.issue = None
        self.jira_user = _jira_user
        self.jira_api_key = _api_key
        self.jira = JIRA(server=self.jira_url, basic_auth=(self.jira_user, self.jira_api_key))
        # self.get_jira_prodcut()
        self.custom_fields = self.get_custom_fields()

    # def get_jira_prodcut(self):
    #     """"""
    #     project = self.jira.project(str(self.project_key))
    #     self.project_name = project.name
    #     print(f"Project: {project.key} - {project.name}")
    # return project

    def get_custom_fields(self) -> dict:
        """
        查询指定项目jira中的自定义字段，smartpush项目是 10559 商品是 10092
        @param project_id: 项目id
        @param jira_obj: 对象
        @return: 返回的是自定义的值对应的id
        :param project_key:
        """
        all_fields = self.jira.fields()
        custom_fields = {}
        for field in all_fields:
            try:
                if field.get('custom'):
                    custom_fields[field['id']] = field['name']
            except:
                continue
        # print(custom_fields)
        return custom_fields

    def get_jira_issues_by_jql(self, filter_id=None, jql=None):
        """
        根据过滤id查询，或者jql查询
        :param filter_id:
        :param jql:
        :return:
        """
        if filter_id:
            filter_obj = self.jira.filter(filter_id)
            jql = filter_obj.jql
        elif jql is None:
            default_jql_str = f'project = SSP'
        try:
            all_issues = {}
            start_at = 0
            max_results = 100  # 每次查询的最大结果数
            while True:
                # 构建 JQL 查询语句，根据项目 key 进行查询
                jql_str = jql if jql else default_jql_str
                print(f"执行查询的jql语句为：{jql_str}")
                # 执行 JQL 查询获取 issues
                issues = self.jira.search_issues(jql_str=jql_str, startAt=start_at, maxResults=max_results)
                if not issues:
                    break
                for issue in issues:
                    self.issue = issue
                    datas = self.custom_value_type()
                    all_issues[self.issue.key] = datas
                if len(issues) < max_results:
                    break
                start_at += max_results
            return all_issues
        except Exception as e:
            raise
            # return {'error': str(e)}

    def custom_value_type(self):
        """
        用于获取自定义字段的key和value值的处理
        :return:
        """
        custom_value_info = {}
        for custom_field_id, custom_field_value in self.issue.raw['fields'].items():
            custom_field_id = self.custom_fields.get(custom_field_id, custom_field_id)
            if custom_field_id in ["comment", "attachment"]:
                custom_field_value = "省略内容..有需要再打开，在这方法过滤：custom_value_type"
            custom_field_value = self.transform_data(custom_field_value)  # 转换数据
            custom_value_info['url'] = self.jira_url + 'browse/' + self.issue.key
            custom_value_info[custom_field_id] = custom_field_value
        return custom_value_info

    def transform_data(self, data):
        """
        转换数据，否则数据冗余的有点多
        :param data:
        :return:
        """
        if not isinstance(data, list) and not isinstance(data, dict):
            return data
        if isinstance(data, list):
            result = []
            for item in data:
                if isinstance(item, dict):
                    for priority_key in ['value', 'name', 'displayName']:
                        if priority_key in item:
                            result.append(item[priority_key])
                            break
                    else:
                        result.append(item)
                else:
                    result.append(item)
            return result
        elif isinstance(data, dict):
            for priority_key in ['value', 'name', 'displayName']:
                if priority_key in data:
                    return data[priority_key]
            return data
        return data

    def update_filter_jql(self, filter_id=None, new_jql=None, double_check=False):

        try:
            if new_jql is None:
                new_jql = get_update_issues_jql()
            # 获取过滤器对象
            filter_obj = self.jira.filter(filter_id)
            # 更新过滤器的 JQL
            if str(filter_id) == '19030' or double_check:
                filter_obj.update(jql=new_jql)
                print(f"过滤器 {filter_id} 的 JQL 已更新为: {new_jql}")
            else:
                print(f"{new_jql} 更新失败！")
        except Exception as e:
            # raise e
            print(f"更新过滤器 JQL 时出错: {e}")

    def product_and_ui_acceptance_notice(self, webhook, datas):
        """
        每周一早上11点通知产品/UI验收
        1、有前端工作量时才需要通知ui
        2、列出对应的ui，没有显示未填写
        :return:
        """
        fixVersions = ""
        content = ""
        for key, value in datas.items():
            if value.get("issuetype") == "产品需求":
                summary = value.get("summary")
                url = value.get("url")
                tester_user_id = self.get_tester_wecom_userid(value.get("测试人员"), test_user)
                product_manager = value.get("产品经理")
                ued = value.get("设计师")
                fixVersions = value.get("fixVersions")
                content += f"> [{key + '-' + summary}]({url})\n PM:{product_manager}\n" \
                           f"UED:{ued}\n测试:{tester_user_id} \n\n "
        content = f"### <font color=\"warning\"> 提醒本周{fixVersions}上线产品需求验收</font> \n" + content
        self.send_wecom_robot_message(webhook, content)

    def registration_coverage_notice(self, webhook, datas):
        """
        测试环境通知登记覆盖率--每周三早上
        1、有后端开发工作量时才提示
        2、并且把填写的链接附上
        :return:
        """
        content = ""
        for key, value in datas.items():
            if value.get("后端工作量") is not None and float(value.get("后端工作量")) > 0:
                summary = value.get("summary")
                url = value.get("url")
                tester_user_id = self.get_tester_wecom_userid(value.get("测试人员"), test_user)
                test_end_time = value.get("测试完成时间（测试环境）")
                content += f"> [{key + '-' + summary}]({url}) \n测试:{tester_user_id} \n测试完成时间：{test_end_time}\n\n "
        content = f"### <font color=\"warning\"> 本周涉及后端需求如下，请分析并登记覆盖率报告，周会前填写</font> \n" + content
        self.send_wecom_robot_message(webhook, content)

    def registration_coverage_notice_every_day(self, webhook, datas):
        """
        1、有后端开发工作量时才提示
        2、并且把填写的链接附上
        :return:
        """
        content = ""
        today = datetime.date.today().strftime('%Y-%m-%d')
        for key, value in datas.items():
            adjusted_test_completion_time = value.get("调整后测试完成时间（测试环境）")
            test_end_time = value.get(
                "测试完成时间（测试环境）") if adjusted_test_completion_time is None else adjusted_test_completion_time
            test_end_text = '测试完成时间（测试环境）' if adjusted_test_completion_time is None else '调整后测试完成时间（测试环境）'
            test_end_time_new = datetime.datetime.strptime(test_end_time, "%Y-%m-%d").strftime(
                '%Y-%m-%d') if test_end_time is not None else None
            summary = value.get("summary")
            url = value.get("url")
            backend_workload = value.get("后端工作量")
            if test_end_time is not None and backend_workload is not None and backend_workload > 0 and test_end_time_new == today:
                tester_user_id = self.get_tester_wecom_userid(value.get("测试人员"), test_user)
                content += f"> [{key + '-' + summary}]({url}) \n后端工作量:{backend_workload}\n测试人员:{tester_user_id} \n{test_end_text}:{test_end_time}\n\n "
        if StringUtils.is_empty(content):
            print(f"*** {today} 无涉及覆盖率登记需求，不发送通知 ***")
            return
        content = f"### <font color=\"warning\"> 涉及后端需求，测试完成后，请分析并登记覆盖率报告</font> \n" + content
        # print(content)
        self.send_wecom_robot_message(webhook, content)

    def bug_not_closed_notice(self, webhook, datas):
        """
        预发环境或者测试环境通知bug还未关闭的需求，每周二，周三执行
        1、'待修复', '修复中', '待验证'
        :return:
        """
        content = ""
        for key, value in datas.items():
            issuelinks = value['issuelinks']
            not_fixed_dict = self.is_bug_not_fixed(issuelinks)
            if not_fixed_dict:
                summary = value.get("summary")
                url = value.get("url")
                tester_user_id = self.get_tester_wecom_userid(value.get("测试人员"), test_user)
                content += f"> [{key + '-' + summary}]({url}) \n暂未修复bug数量：{len(not_fixed_dict)}\n测试:{tester_user_id} \n\n "
        if StringUtils.is_empty(content):
            print("无待修复bug..不发送通知")
            return
        content = f"### <font color=\"warning\"> 提醒本周上线需求暂未修复缺陷，请尽快确认</font> \n" + content
        self.send_wecom_robot_message(webhook, content)
        # print(content)

    def modify_the_online_status_of_jira_notice(self, webhook, datas):
        """
        每周四上线完通知修改jira上线日期、上线状态、自动化工作量填写 -- 每周四下午4点
        1、显示jira状态
        2、jira链接
        3、测试人员
        :return:
        """
        content = ""
        fixVersions = ""
        for key, value in datas.items():
            summary = value.get("summary")
            url = value.get("url")
            tester_user_id = self.get_tester_wecom_userid(value.get("测试人员"), test_user)
            status = value.get("status")
            actually_online_time = value.get("实际上线时间")
            automated_testing_workload = value.get("自动化测试工作量")
            automation_saves_labor_time = value.get("自动化节省工时")
            fixVersions = value.get("fixVersions")
            content += f"> [{key + '-' + summary}]({url}) \n状态：{status}\n实际上线时间：{actually_online_time}\n自动化测试工作量：{automated_testing_workload}\n自动节省工时：{automation_saves_labor_time}\n" \
                       f"测试:{tester_user_id}\n版本号：{fixVersions} \n\n "
        content = f"### <font color=\"warning\"> 本周版本需求已上线，请检查并更新jira数据，进行版本收尾</font> \n" + content
        self.send_wecom_robot_message(webhook, content)

    def get_tester_wecom_userid(self, tester, user_data):
        """
        获取名字用于群里@使用
        :param user_data: 用户id映射关系
        :param tester: 传名字
        :param data:数据结构
        :return:
        """
        mobile_string = ""
        if tester is None:
            return None
        for name in tester:
            user_id = user_data.get(name, None)
            mobile_string += f"<@{user_id}>"
        return mobile_string

    def is_bug_not_fixed(self, issuelinks) -> dict:
        """
        查询未修复的bug
        :param issuelinks:
        :return:
        """
        not_fixed_bug_dict = {}
        not_fixed_status_list = ['待修复', '修复中', '待验证']
        for issue in issuelinks:
            if issue.get('type').get('id') == '10003':  # bug类型
                status_name = issue['inwardIssue']['fields']['status']['name']
                bug_key = issue['inwardIssue']['key']
                bug_name = issue['inwardIssue']['fields']['summary']
                if status_name in not_fixed_status_list:
                    not_fixed_bug_dict[bug_key] = bug_name
        return not_fixed_bug_dict

    def send_wecom_robot_message(self, webhook_url, content, msg_type='markdown'):
        headers = {
            'Content-Type': 'application/json'
        }
        if msg_type == 'text':
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
        elif msg_type == 'markdown':
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
        elif msg_type == 'link':
            if not isinstance(content, dict) or 'title' not in content or 'text' not in content or 'url' not in content:
                raise ValueError("link类型消息content必须是包含title、text、url的字典")
            data = {
                "msgtype": "link",
                "link": content
            }
        elif msg_type == 'file':
            if not isinstance(content, dict) or 'media_id' not in content:
                raise ValueError("file类型消息content必须是包含media_id的字典")
            data = {
                "msgtype": "file",
                "file": content
            }
        elif msg_type == 'image':
            if not isinstance(content, dict) or 'media_id' not in content:
                raise ValueError("image类型消息content必须是包含media_id的字典")
            data = {
                "msgtype": "image",
                "image": content
            }
        elif msg_type == 'news':
            if not isinstance(content, list):
                raise ValueError("news类型消息content必须是列表")
            for item in content:
                if not isinstance(item,
                                  dict) or 'title' not in item or 'description' not in item or 'url' not in item or 'picurl' not in item:
                    raise ValueError("news类型消息content列表中的每个元素必须是包含title、description、url、picurl的字典")
            data = {
                "msgtype": "news",
                "news": {
                    "articles": content
                }
            }
        else:
            raise ValueError("不支持的消息类型，请选择text、markdown、link、file、image、news")

        try:
            response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            print("发送企微消息成功!")
            return response.json()
        except requests.RequestException as e:
            print(f"请求出错: {e}")
            return None
        except ValueError as e:
            print(f"解析响应出错: {e}")
            return None
