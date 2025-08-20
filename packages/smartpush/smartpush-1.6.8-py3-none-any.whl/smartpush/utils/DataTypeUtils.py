import re
from datetime import datetime


class DataTypeUtils:

    def check_email_format(self, email):
        # 检查邮箱是否符合格式
        if email != "" or email is not None:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))

    def check_time_format(self, time_str, precision="s"):
        # 检查时间是否符合格式，并校验是精确到秒还是分
        if precision == 's':
            try:
                # 尝试按照精确到秒的格式解析
                datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                return True
            except ValueError:
                return False
        elif precision == 'm':
            try:
                # 尝试按照精确到分钟的格式解析
                datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                return True
            except ValueError:
                return False
        else:
            raise ValueError("Invalid precision parameter. Use 's' for seconds or 'm' for minutes.")
