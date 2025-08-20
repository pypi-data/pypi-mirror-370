class StringUtils:
    @staticmethod
    def to_upper(s):
        """
        将字符串转换为大写
        :param s: 输入的字符串
        :return: 转换为大写后的字符串
        """
        return s.upper() if isinstance(s, str) else s

    @staticmethod
    def to_lower(s):
        """
        将字符串转换为小写
        :param s: 输入的字符串
        :return: 转换为小写后的字符串
        """
        return s.lower() if isinstance(s, str) else s

    @staticmethod
    def strip(s):
        """
        去除字符串两端的空白字符
        :param s: 输入的字符串
        :return: 去除两端空白字符后的字符串
        """
        return s.strip() if isinstance(s, str) else s

    @staticmethod
    def is_digit(s):
        """
        判断字符串是否只包含数字
        :param s: 输入的字符串
        :return: 如果只包含数字返回 True，否则返回 False
        """
        return s.isdigit() if isinstance(s, str) else False

    @staticmethod
    def substring(s, start, end=None):
        """
        截取字符串的子字符串
        :param s: 输入的字符串
        :param start: 起始索引
        :param end: 结束索引（可选）
        :return: 截取的子字符串
        """
        return s[start:end] if isinstance(s, str) else s

    @staticmethod
    def replace(s, old, new):
        """
        替换字符串中的指定子字符串
        :param s: 输入的字符串
        :param old: 要替换的旧子字符串
        :param new: 替换后的新子字符串
        :return: 替换后的字符串
        """
        return s.replace(old, new) if isinstance(s, str) else s

    @staticmethod
    def split(s, sep=None):
        """
        根据指定分隔符分割字符串
        :param s: 输入的字符串
        :param sep: 分隔符（可选）
        :return: 分割后的字符串列表
        """
        return s.split(sep) if isinstance(s, str) else s

    @staticmethod
    def is_empty(s):
        """
        判断字符串是否为空
        :param s: 输入的字符串
        :return: 如果字符串为空或仅包含空白字符返回 True，否则返回 False
        """
        return not s or s.isspace() if isinstance(s, str) or s is None else False

    @staticmethod
    def contains(s, sub):
        """
        判断字符串是否包含指定子字符串
        :param s: 输入的字符串
        :param sub: 要检查的子字符串
        :return: 如果包含返回 True，否则返回 False
        """
        return sub in s if isinstance(s, str) and isinstance(sub, str) else False

    @staticmethod
    def reverse(s):
        """
        反转字符串
        :param s: 输入的字符串
        :return: 反转后的字符串
        """
        return s[::-1] if isinstance(s, str) else s

    @staticmethod
    def count_substring(s, sub):
        """
        统计子字符串在字符串中出现的次数
        :param s: 输入的字符串
        :param sub: 要统计的子字符串
        :return: 子字符串出现的次数
        """
        return s.count(sub) if isinstance(s, str) and isinstance(sub, str) else 0

    @staticmethod
    def startswith(s, prefix):
        """
        判断字符串是否以指定前缀开头
        :param s: 输入的字符串
        :param prefix: 前缀字符串
        :return: 如果以指定前缀开头返回 True，否则返回 False
        """
        return s.startswith(prefix) if isinstance(s, str) and isinstance(prefix, str) else False

    @staticmethod
    def endswith(s, suffix):
        """
        判断字符串是否以指定后缀结尾
        :param s: 输入的字符串
        :param suffix: 后缀字符串
        :return: 如果以指定后缀结尾返回 True，否则返回 False
        """
        return s.endswith(suffix) if isinstance(s, str) and isinstance(suffix, str) else False

    @staticmethod
    def truncate_string(input_string):
        if len(input_string) > 30:
            return input_string[:15]
        return input_string
