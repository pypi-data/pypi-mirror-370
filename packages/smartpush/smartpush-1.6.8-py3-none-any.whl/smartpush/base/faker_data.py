from faker import Faker
from user_agents import parse
import random

# 中文类型faker
fake = Faker(locale='zh_CN')
fake_en = Faker(locale='en_US')


# print("可以fake的内容:",dir(fake))

# """地理信息类"""
# city_suffix = fake.city_suffix()  # 生成市、县的后缀，例如：'市'
# country = fake.country()  # 生成国家名称，例如：'中国'
# country_code = fake.country_code()  # 生成国家编码，例如：'CN'
# district = fake.district()  # 生成区的名称，例如：'朝阳区'
# geo_coordinate = fake.geo_coordinate()  # 生成地理坐标，例如：'(31.692720, 88.092434)'
# latitude = fake.latitude()  # 生成纬度，例如：31.692720
# longitude = fake.longitude()  # 生成经度，例如：88.092434
# postcode = fake.postcode()  # 生成邮编，例如：'100000'
# province = fake.province()  # 生成省份名称，例如：'北京市'
# address = fake.address()  # 生成详细地址，例如：'北京市朝阳区'
# street_address = fake.street_address()  # 生成街道地址，例如：'人民路123号'
# street_name = fake.street_name()  # 生成街道名，例如：'人民路'
# street_suffix = fake.street_suffix()  # 生成街、路的后缀，例如：'路'

# """基础信息类"""
# ssn = fake.ssn()  # 生成身份证号，例如：'510181199503077777'
# bs = fake.bs()  # 随机公司服务名，例如：'技术支持'
# company = fake.company()  # 随机公司名（长），例如：'北京百度在线网络技术有限公司'
# company_prefix = fake.company_prefix()  # 随机公司名（短），例如：'百度'
# company_suffix = fake.company_suffix()  # 公司性质，例如：'信息有限公司'
# credit_card_expire = fake.credit_card_expire()  # 随机信用卡到期日，例如：'12/25'
# credit_card_full = fake.credit_card_full()  # 生成完整信用卡信息，例如：'VISA 16 digits 04/24 CVV:022'
# credit_card_number = fake.credit_card_number()  # 信用卡号，例如：'4539853637484'
# credit_card_provider = fake.credit_card_provider()  # 信用卡类型，例如：'VISA 16 digit'
# credit_card_security_code = fake.credit_card_security_code()  # 信用卡安全码，例如：'356'
# job = fake.job()  # 随机职位，例如：'市场营销经理'
# first_name_female = fake.first_name_female()  # 女性名，例如：'丽娜'
# first_name_male = fake.first_name_male()  # 男性名，例如：'伟'
# last_name_female = fake.last_name_female()  # 女姓，例如：'王'
# last_name_male = fake.last_name_male()  # 男姓，例如：'张'
# name = fake.name()  # 随机生成全名，例如：'张丽'
# name_female = fake.name_female()  # 男性全名，例如：'杨丽'
# name_male = fake.name_male()  # 女性全名，例如：'王伟'
# phone_number = fake.phone_number()  # 随机生成手机号，例如：'13912345678'
# phonenumber_prefix = fake.phonenumber_prefix()  # 随机生成手机号段，例如：'139'

# """计算机基础、Internet信息类、Email"""
# ascii_company_email = fake.ascii_company_email()  # 随机ASCII公司邮箱名，例如：'example_company'
# ascii_email = fake.ascii_email()  # 随机ASCII邮箱，例如：'example@example.com'
# company_email = fake.company_email()  # 随机公司邮箱
# email = fake.email()  # 随机邮箱
# safe_email = fake.safe_email()  # 安全邮箱


# """网络基础信息类"""
# domain_name = fake.domain_name()  # 生成域名，例如：'smith.com'
# domain_word = fake.domain_word()  # 生成域词(即，不包含后缀)，例如：'example'
# ipv4 = fake.ipv4()  # 随机IP4地址，例如：'192.168.1.1'
# ipv6 = fake.ipv6()  # 随机IP6地址，例如：'2001:0db8:85a3:0000:0000:8a2e:0370:7334'
# mac_address = fake.mac_address()  # 随机MAC地址，例如：'5e:ff:56:8c:13:5f'
# tld = fake.tld()  # 网址域名后缀(.com,.net.cn,等等，不包括.)，例如：'com'
# uri = fake.uri()  # 随机URI地址，例如：'http://www.example.com/path/to/page'
# uri_extension = fake.uri_extension()  # 网址文件后缀，例如：'.html'
# uri_page = fake.uri_page()  # 网址文件（不包含后缀），例如：'index'
# uri_path = fake.uri_path()  # 网址文件路径（不包含文件名），例如：'/path/to'
# url = fake.url()  # 随机URL地址，例如：'http://www.example.com'
# user_name = fake.user_name()  # 随机用户名，例如：'john_doe'
# image_url = fake.image_url()  # 随机URL地址，例如：'http://www.example.com/image.jpg'

# """
# 浏览器信息类
# """
# chrome = fake.chrome()  # 随机生成Chrome的浏览器user_agent信息
# firefox = fake.firefox()  # 随机生成FireFox的浏览器user_agent信息
# internet_explorer = fake.internet_explorer()  # 随机生成IE的浏览器user_agent信息
# opera = fake.opera()  # 随机生成Opera的浏览器user_agent信息
# safari = fake.safari()  # 随机生成Safari的浏览器user_agent信息
# linux_platform_token = fake.linux_platform_token()  # 随机Linux信息
# user_agent = fake.user_agent()  # 随机user_agent信息

# """
# 数字类
# """
# numerify = fake.numerify()  # 三位随机数字，例如：'123'
# random_digit = fake.random_digit()  # 0~9随机数，例如：'7'
# random_digit_not_null = fake.random_digit_not_null()  # 1~9的随机数，例如：'3'
# random_int = fake.random_int()  # 随机数字，默认0~9999，可以通过设置min,max来设置，例如：'567'
# random_number = fake.random_number(digits=5)  # 随机数字，参数digits设置生成的数字位数，例如：'12345'
# pyint = fake.pyint()  # 随机Int数字，例如：'987'
# pyfloat = fake.pyfloat(left_digits=5, right_digits=2, positive=True)  # 随机Float数字，例如：'12345.67'
# pydecimal = fake.pydecimal()  # 随机Decimal数字，例如：Decimal('123.45')

# """
# 文本、加密类
# """
# pystr = fake.pystr()  # 随机字符串，例如：'abc123'
# random_element = fake.random_element()  # 随机字母，例如：'a'
# random_letter = fake.random_letter()  # 随机字母，例如：'b'
# paragraph = fake.paragraph()  # 随机生成

# """时间信息类"""
# date = fake.date()  # 随机日期
# date_between = fake.date_between(start_date='-30y', end_date='today')  # 随机生成指定范围内日期，例如：datetime.date(1998, 4, 3)
# date_object = fake.date_object()  # 随机生产从1970-1-1到指定日期的随机日期，例如：datetime.date(1985, 3, 19)
# date_time = fake.date_time()  # 随机生成指定时间（1970年1月1日至今），例如：datetime.datetime(2003, 5, 23, 16, 45, 40)
# date_time_ad = fake.date_time_ad()  # 生成公元1年到现在的随机时间，例如：datetime.datetime(2005, 12, 2, 19, 25, 46)
# date_time_between = fake.date_time_between(start_date='-30y', end_date='now')  # 随机生成指定范围内日期，用法同dates
# future_date = fake.future_date(end_date='+30d')  # 未来日期，例如：datetime.date(2023, 2, 17)
# future_datetime = fake.future_datetime(end_date='+30d')  # 未来时间，例如：datetime.datetime(2023, 2, 17, 20, 48, 35)
# month = fake.month()  # 随机月份，例如：'04'
# month_name = fake.month_name()  # 随机月份（英文），例如：'December'
# past_date = fake.past_date(start_date='-30d')  # 随机生成已经过去的日期，例如：datetime.date(2023, 1, 18)
# past_datetime = fake.past_datetime(start_date='-30d')  # 随机生成已经过去的时间，例如：datetime.datetime(2023, 1, 18, 20, 48, 35)
# time = fake.time()  # 随机24小时时间，例如：datetime.time(13, 20, 10)
# timedelta = fake.time_delta()  # 随机获取时间差，例如：datetime.timedelta(days=3, seconds=86254)
# time_object = fake.time_object()  # 随机24小时时间，time对象，例如：datetime.time(21, 47)
# time_series = fake.time_series()  # 随机TimeSeries对象，例如：<faker.providers.date_time.Provider object at 0x7fc4bca6d9d0>
# timezone = fake.timezone()  # 随机时区，例如：'Asia/Shanghai'
# unix_time = fake.unix_time()  # 随机Unix时间，例如：659312340
# year = fake.year()  # 随机年份，例如：'1998'
class FakeDataGenerator:

    def __init__(self, seed=None, locale='zh_CN'):
        """初始化Faker实例并设置本地化"""
        Faker.seed(seed)
        self.fake = Faker(locale)
        # fake.seed(seed)
        self.fake_en = Faker('en_US')  # 用于生成英文国家名

        # 生成用户代理并解析
        self._user_agent = self.fake.user_agent()
        self._parsed_ua = parse(self._user_agent)

    @property
    def user_agent(self):
        return self._user_agent

    @property
    def fake_currency(self):
        return self.fake.currency()[0]

    @property
    def fake_city(self):
        return self.fake.city()

    @property
    def fake_city_suffix(self):
        return self.fake.city_suffix()

    @property
    def fake_country(self):
        return self.fake_en.country()

    @property
    def fake_country_code(self):
        return self.fake.country_code()

    @property
    def fake_district(self):
        return self.fake.district()

    @property
    def fake_latitude(self):
        return self.fake.latitude()

    @property
    def fake_longitude(self):
        return self.fake.longitude()

    @property
    def fake_postcode(self):
        return self.fake.postcode()

    @property
    def fake_province(self):
        return self.fake.province()

    @property
    def fake_address(self):
        return self.fake.address()

    @property
    def fake_street_address(self):
        return self.fake.street_address()

    @property
    def fake_street_name(self):
        return self.fake.street_name()

    @property
    def fake_street_suffix(self):
        return self.fake.street_suffix()

    @property
    def fake_ssn(self):
        return self.fake.ssn()

    @property
    def fake_bs(self):
        return self.fake.bs()

    @property
    def fake_company(self):
        return self.fake.company()

    @property
    def fake_company_prefix(self):
        return self.fake.company_prefix()

    @property
    def fake_company_suffix(self):
        return self.fake.company_suffix()

    @property
    def fake_credit_card_expire(self):
        return self.fake.credit_card_expire()

    @property
    def fake_credit_card_full(self):
        return str(self.fake.credit_card_full())

    @property
    def fake_credit_card_number(self):
        return self.fake.credit_card_number()

    @property
    def fake_credit_card_provider(self):
        return self.fake.credit_card_provider()

    @property
    def fake_credit_card_security_code(self):
        return self.fake.credit_card_security_code()

    @property
    def fake_job(self):
        return self.fake.job()

    @property
    def fake_gender(self):
        return random.choice(["u", "f", "m"])

    @property
    def fake_first_name_female(self):
        return "AutoTest-" + self.fake.first_name_female()

    @property
    def fake_first_name_male(self):
        return "AutoTest-" + self.fake.first_name_male()

    @property
    def fake_last_name_female(self):
        return "AutoTest-" + self.fake.last_name_female()

    @property
    def fake_last_name_male(self):
        return "AutoTest-" + self.fake.last_name_male()

    @property
    def fake_name(self):
        return "AutoTest-" + self.fake.name()

    @property
    def fake_name_female(self):
        return "AutoTest-" + self.fake.name_female()

    @property
    def fake_name_male(self):
        return "AutoTest-" + self.fake.name_male()

    @property
    def fake_phone_number(self):
        return self.fake.phone_number()

    @property
    def fake_phonenumber_prefix(self):
        return self.fake.phonenumber_prefix()

    @property
    def fake_ascii_company_email(self):
        return self.fake.ascii_company_email()

    @property
    def fake_ascii_email(self):
        return self.fake.ascii_email()

    @property
    def fake_company_email(self):
        return self.fake.company_email()

    @property
    def fake_email(self):
        return "AutoTest-" + self.fake.email()

    @property
    def fake_safe_email(self):
        return self.fake.safe_email()

    @property
    def fake_domain_name(self):
        return self.fake.domain_name()

    @property
    def fake_domain_word(self):
        return self.fake.domain_word()

    @property
    def fake_ipv4(self):
        return self.fake.ipv4()

    @property
    def fake_ipv6(self):
        return self.fake.ipv6()

    @property
    def fake_mac_address(self):
        return self.fake.mac_address()

    @property
    def fake_port_number(self):
        return self.fake.port_number()

    @property
    def fake_tld(self):
        return self.fake.tld()

    @property
    def fake_uri(self):
        return self.fake.uri()

    @property
    def fake_uri_extension(self):
        return self.fake.uri_extension()

    @property
    def fake_uri_page(self):
        return self.fake.uri_page()

    @property
    def fake_uri_path(self):
        return self.fake.uri_path()

    @property
    def fake_url(self):
        return self.fake.url()

    @property
    def fake_user_name(self):
        return "AutoTest-" + self.fake.user_name()

    @property
    def fake_image_url(self):
        return self.fake.image_url()

    @property
    def fake_linux_platform_token(self):
        return self.fake.linux_platform_token()

    @property
    def fake_browser(self):
        return self._parsed_ua.browser.family

    @property
    def fake_browser_version(self):
        return '.'.join(map(str, self._parsed_ua.browser.version[:2]))

    @property
    def fake_os(self):
        return self._parsed_ua.os.family

    @property
    def fake_os_version(self):
        return '.'.join(map(str, self._parsed_ua.os.version[:2]))

    @property
    def fake_device_type(self):
        return random.choice(["desktop", "mobile"])

    @property
    def fake_network(self):
        return random.choice(["4g", "3g", "2g"])

    @property
    def fake_numerify(self):
        return self.fake.numerify()

    @property
    def fake_random_digit(self):
        return self.fake.random_digit()

    @property
    def fake_random_digit_not_null(self):
        return self.fake.random_digit_not_null()

    @property
    def fake_random_int(self):
        return self.fake.random_int()

    @property
    def fake_random_number(self):
        return self.fake.random_number(digits=5)

    @property
    def fake_random_long_number(self):
        return self.fake.random_number(digits=26)

    @property
    def fake_random_ten_number(self):
        return self.fake.random_number(digits=10)

    @property
    def fake_pyint(self):
        return self.fake.pyint()

    @property
    def fake_pyfloat(self):
        return self.fake.pyfloat(left_digits=5, right_digits=4, positive=True)

    @property
    def fake_pydecimal(self):
        return self.fake.pydecimal()

    @property
    def fake_pystr(self):
        return self.fake.pystr()

    @property
    def fake_version(self):
        return f"AutoTest-1.1.{self.fake.pyfloat(left_digits=8, right_digits=4, positive=True)}{self.fake.pyfloat(left_digits=6, right_digits=8, positive=True)}"

    @property
    def fake_random_element(self):
        return self.fake.random_element()

    @property
    def fake_random_letter(self):
        return self.fake.random_letter()

    @property
    def fake_paragraph(self):
        return self.fake.paragraph()

    @property
    def fake_sentence(self):
        return self.fake.sentence()

    @property
    def fake_word(self):
        return self.fake.word()

    @property
    def fake_boolean(self):
        return self.fake.boolean()

    @property
    def fake_language(self):
        return self.fake.language_code()

    @property
    def fake_locale_language(self):
        return self.fake.locale()

    @property
    def fake_md5(self):
        return self.fake.md5()

    @property
    def fake_password(self):
        return self.fake.password()

    @property
    def fake_sha1(self):
        return self.fake.sha1()

    @property
    def fake_sha256(self):
        return self.fake.sha256()

    @property
    def fake_uuid4(self):
        return self.fake.uuid4()

    @property
    def fake_date(self):
        return self.fake.date()

    @property
    def fake_date_between(self):
        return self.fake.date_between(start_date='-30y', end_date='today')

    @property
    def fake_date_object(self):
        return self.fake.date_object()

    @property
    def fake_date_time(self):
        return self.fake.date_time()

    @property
    def fake_date_time_ad(self):
        return self.fake.date_time_ad()

    @property
    def fake_date_time_between(self):
        return self.fake.date_time_between(start_date='-30y', end_date='now')

    @property
    def fake_future_date(self):
        return self.fake.future_date(end_date='+30d')

    @property
    def fake_future_datetime(self):
        return self.fake.future_datetime(end_date='+30d')

    @property
    def fake_month(self):
        return self.fake.month()

    @property
    def fake_month_name(self):
        return self.fake.month_name()

    @property
    def fake_past_date(self):
        return self.fake.past_date(start_date='-30d')

    @property
    def fake_past_datetime(self):
        return self.fake.past_datetime(start_date='-30d')

    @property
    def fake_time(self):
        return self.fake.time()

    @property
    def fake_timedelta(self):
        return self.fake.time_delta()

    @property
    def fake_time_object(self):
        return self.fake.time_object()

    @property
    def fake_timezone(self):
        return self.fake.timezone()

    @property
    def fake_unix_time(self):
        return self.fake.unix_time()

    @property
    def fake_year(self):
        return self.fake.year()

    @property
    def fake_width(self):
        return random.randint(800, 4000)

    @property
    def fake_height(self):
        return random.randint(600, 2500)

    def generate_user_data(self):
        """
        生成完整的用户测试数据
        """
        user_agent = self.fake.user_agent()
        parsed_ua = parse(user_agent)

        return {
            'user_agent': user_agent,
            'fake_currency': self.fake.currency()[0],
            'fake_city': self.fake.city(),
            'fake_city_suffix': self.fake.city_suffix(),
            'fake_country': self.fake_en.country(),
            'fake_country_code': self.fake.country_code(),
            'fake_district': self.fake.district(),
            'fake_latitude': self.fake.latitude(),
            'fake_longitude': self.fake.longitude(),
            'fake_postcode': self.fake.postcode(),
            'fake_province': self.fake.province(),
            'fake_address': self.fake.address(),
            'fake_street_address': self.fake.street_address(),
            'fake_street_name': self.fake.street_name(),
            'fake_street_suffix': self.fake.street_suffix(),
            'fake_ssn': self.fake.ssn(),
            'fake_bs': self.fake.bs(),
            'fake_company': self.fake.company(),
            'fake_company_prefix': self.fake.company_prefix(),
            'fake_company_suffix': self.fake.company_suffix(),
            'fake_credit_card_expire': self.fake.credit_card_expire(),
            'fake_credit_card_full': str(self.fake.credit_card_full()),
            'fake_credit_card_number': self.fake.credit_card_number(),
            'fake_credit_card_provider': self.fake.credit_card_provider(),
            'fake_credit_card_security_code': self.fake.credit_card_security_code(),
            'fake_job': self.fake.job(),
            'fake_gender': random.choice(["u", "f", "m"]),
            'fake_first_name_female': "AutoTest-" + self.fake.first_name_female(),
            'fake_first_name_male': "AutoTest-" + self.fake.first_name_male(),
            'fake_last_name_female': "AutoTest-" + self.fake.last_name_female(),
            'fake_last_name_male': "AutoTest-" + self.fake.last_name_male(),
            'fake_name': "AutoTest-" + self.fake.name(),
            'fake_name_female': "AutoTest-" + self.fake.name_female(),
            'fake_name_male': "AutoTest-" + self.fake.name_male(),
            'fake_phone_number': self.fake.phone_number(),
            'fake_phonenumber_prefix': self.fake.phonenumber_prefix(),
            'fake_ascii_company_email': self.fake.ascii_company_email(),
            'fake_ascii_email': self.fake.ascii_email(),
            'fake_company_email': self.fake.company_email(),
            'fake_email': "AutoTest-" + self.fake.email(),
            'fake_safe_email': self.fake.safe_email(),
            'fake_domain_name': self.fake.domain_name(),
            'fake_domain_word': self.fake.domain_word(),
            'fake_ipv4': self.fake.ipv4(),
            'fake_ipv6': self.fake.ipv6(),
            'fake_mac_address': self.fake.mac_address(),
            'fake_port_number': self.fake.port_number(),
            'fake_tld': self.fake.tld(),
            'fake_uri': self.fake.uri(),
            'fake_uri_extension': self.fake.uri_extension(),
            'fake_uri_page': self.fake.uri_page(),
            'fake_uri_path': self.fake.uri_path(),
            'fake_url': self.fake.url(),
            'fake_user_name': "AutoTest-" + self.fake.user_name(),
            'fake_image_url': self.fake.image_url(),
            'fake_linux_platform_token': self.fake.linux_platform_token(),
            'fake_browser': parsed_ua.browser.family,
            'fake_browser_version': '.'.join(map(str, parsed_ua.browser.version[:2])),
            'fake_os': parsed_ua.os.family,
            'fake_os_version': '.'.join(map(str, parsed_ua.os.version[:2])),
            'fake_device_type': random.choice(["desktop", "mobile"]),
            'fake_network': random.choice(["4g", "3g", "2g"]),
            'fake_numerify': self.fake.numerify(),
            'fake_random_digit': self.fake.random_digit(),
            'fake_random_digit_not_null': self.fake.random_digit_not_null(),
            'fake_random_int': self.fake.random_int(),
            'fake_random_number': self.fake.random_number(digits=5),
            'fake_random_long_number': self.fake.random_number(digits=26),
            'fake_random_ten_number': self.fake.random_number(digits=10),
            'fake_pyint': self.fake.pyint(),
            'fake_pyfloat': self.fake.pyfloat(left_digits=5, right_digits=4, positive=True),
            'fake_pydecimal': self.fake.pydecimal(),
            'fake_pystr': self.fake.pystr(),
            'fake_version': f"AutoTest-1.1.{self.fake.pyfloat(left_digits=8, right_digits=4, positive=True)}{self.fake.pyfloat(left_digits=6, right_digits=8, positive=True)}",
            'fake_random_element': self.fake.random_element(),
            'fake_random_letter': self.fake.random_letter(),
            'fake_paragraph': self.fake.paragraph(),
            'fake_sentence': self.fake.sentence(),
            'fake_word': self.fake.word(),
            'fake_boolean': self.fake.boolean(),
            'fake_language': self.fake.language_code(),
            'fake_locale_language': self.fake.locale(),
            'fake_md5': self.fake.md5(),
            'fake_password': self.fake.password(),
            'fake_sha1': self.fake.sha1(),
            'fake_sha256': self.fake.sha256(),
            'fake_uuid4': self.fake.uuid4(),
            'fake_date': self.fake.date(),
            'fake_date_between': self.fake.date_between(start_date='-30y', end_date='today'),
            'fake_date_object': self.fake.date_object(),
            'fake_date_time': self.fake.date_time(),
            'fake_date_time_ad': self.fake.date_time_ad(),
            'fake_date_time_between': self.fake.date_time_between(start_date='-30y', end_date='now'),
            'fake_future_date': self.fake.future_date(end_date='+30d'),
            'fake_future_datetime': self.fake.future_datetime(end_date='+30d'),
            'fake_month': self.fake.month(),
            'fake_month_name': self.fake.month_name(),
            'fake_past_date': self.fake.past_date(start_date='-30d'),
            'fake_past_datetime': self.fake.past_datetime(start_date='-30d'),
            'fake_time': self.fake.time(),
            'fake_timedelta': self.fake.time_delta(),
            'fake_time_object': self.fake.time_object(),
            'fake_timezone': self.fake.timezone(),
            'fake_unix_time': self.fake.unix_time(),
            'fake_year': self.fake.year(),
            'fake_width': random.randint(800, 4000),
            'fake_height': random.randint(600, 2500)
        }
