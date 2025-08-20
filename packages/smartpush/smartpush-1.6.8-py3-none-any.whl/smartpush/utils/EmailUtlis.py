#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import random
import re
import ssl
from datetime import timedelta, datetime
from urllib.parse import parse_qs
from retry import retry
import imapclient
import pyzmail
import requests
from bs4 import BeautifulSoup
from urllib import parse

junkEmail, allEmail = "[Gmail]/垃圾邮件", "[Gmail]/所有邮件"


def forParseEmailContent(UIDs, isReturnHtml=False):
    """
    解析邮件内容
    @param UIDs:
    @return:
    """
    global _subject, _sender, _from_email, _recipient, _receiveDate, _replay
    messageInfo = {}
    subjectList = []
    if len(UIDs) > 0:
        rawMessages = imapObj.fetch(UIDs, ['BODY[]'])

        for uid in UIDs:
            message = pyzmail.PyzMessage.factory(rawMessages[uid][b'BODY[]'])
            # 解析邮件内容
            _subject = message.get_subject()
            subjectList.append(_subject)
            _sender = message.get_addresses('from')[0][0]
            _from_email = message.get_addresses('from')[0][1]
            _recipient = message.get_addresses('to')[0][0]
            if message.get_addresses('reply-to'):
                _replay = message.get_addresses('reply-to')[0][0]
            _receiveDate = message.get('date')
            tempData = {"sender": _sender, "from_email": _from_email, "recipient": _recipient,
                        "receiveAddress": _replay if _replay else None, "receiveDate": _receiveDate}
            if len(UIDs) == 1:
                messageInfo.update({_subject: tempData})
            else:
                if messageInfo.get(_subject) is None:
                    messageInfo.update({_subject: [tempData]})
                else:
                    tempList = messageInfo.get(_subject)
                    tempList.append(tempData)
                    messageInfo.update({_subject: tempList})
            # html内容解析
            if isReturnHtml:
                htmlBody = message.html_part.get_payload().decode(message.html_part.charset)
                # print('邮件html:', htmlBody)

    if not isReturnHtml:
        # print("------------------")
        # print("邮件主旨:" + _subject)
        # print("发件人:" + _sender)
        # print("发件邮箱:" + _from_email)
        # print("收件人邮箱:" + _recipient)
        # print("回复邮箱:" + _replay)
        # print('接收邮件日期：' + _receiveDate)
        return messageInfo
    else:
        return messageInfo, htmlBody


def selectFolderGetUids(imapObj, foldersName, text=None):
    """
    @param imapObj:邮件对象
    @param foldersName: 文件夹
    @param text: 搜索文本
    @return: Uid，文件的id
    """
    imapObj.select_folder(foldersName, readonly=True)
    # print(f"在  【{foldersName}】 中搜索关键词--->  ：{text}")
    if text:
        # 通过标题搜索
        UIDs = imapObj.gmail_search(text)
    else:
        # 查找所有
        UIDs = imapObj.gmail_search(u'All')
    return UIDs


def loginShowFoldersEmail(email, password):
    # 登录邮件
    # imaplib._MAXLINE = 10000000  # 最大行数限制
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    imapObj = imapclient.IMAPClient('imap.gmail.com', ssl=True, ssl_context=context)
    imapObj.login(email, password)
    folders = imapObj.list_folders()
    print("所有的邮件文件夹:", [folder[2] for folder in folders])
    return imapObj


def getTodayDateTime():
    # 获取当天日期
    since = datetime.utcnow() - timedelta(minutes=1)
    receiveTime = since.strftime('%d-%b-%Y')
    return receiveTime


def fetchEmail(imapObj, UIDs):
    """
    标识为已读（打开邮件）
    @param imapObj:
    @param UIDs:
    @return:
    """
    imapObj.fetch(UIDs, ['BODY[]'])
    return True


def assertEmail(emailProperty=None, is_check_email_property=True):
    errors = []
    for temp in emailProperty:
        _subject = list(temp.keys())[0]
        # print("\n----执行遍历断言---->  ", _subject)
        try:
            UIDs = selectFolderGetUids(imapObj, allEmail, _subject)
            assert UIDs
        except AssertionError:
            UIDs = selectFolderGetUids(imapObj, junkEmail, _subject)
            try:
                assert UIDs
            except AssertionError:
                errors.append({_subject: "未收到邮件"})
                is_check_email_property = False
                # raise AssertionError(f"找不到相符的邮件内容：{_subject}")
        finally:
            # 断言回复邮箱和发件人
            if is_check_email_property:
                EmailContentAll = forParseEmailContent(UIDs)
                property_result = assertEmailProperty(temp[_subject], EmailContentAll[_subject])
                if len(property_result) > 0:
                    errors.append({_subject: property_result})
    return [True, "邮件内容断言成功"] if len(errors) == 0 else [False, {"邮件内容断言失败": errors}]


def assertEmailProperty(emailProperty, ParseEmailContent):
    """
    断言邮件内容
    @param emailProperty:
    @param ParseEmailContent:assertEmail
    @return:
    """
    property_errors = []
    # print("原始数据", ParseEmailContent)
    if isinstance(ParseEmailContent, list):
        _parseEmailContent = ParseEmailContent[0]
    else:
        # 新增-发件人、回复邮箱断言
        _parseEmailContent = ParseEmailContent
    if emailProperty.get('sender') != _parseEmailContent.get('sender'):
        property_errors.append(
            ["发件人断言失败", {"预期": emailProperty.get('sender'), "实际": _parseEmailContent.get('sender')}])
    if emailProperty.get('receiveAddress') != _parseEmailContent.get('receiveAddress'):
        property_errors.append(["回复邮箱断言失败",
                                {"预期": emailProperty.get('receiveAddress'),
                                 "实际": _parseEmailContent.get('receiveAddress')}])
    return property_errors


def getRandomHyperlinksInHtml(EmailContent):
    """
    获取html中的随机超链接
    @param html:
    @return:
    """
    flag = 1
    # page = BeautifulSoup(EmailContent[1], features="html.parser")
    pages = BeautifulSoup(EmailContent[1], features="html.parser")
    alinks = pages.findAll('a')
    new_links = []
    for url in alinks:
        if url.get('href', None) != '#' and 'mailto:' not in url.get('href', None) and url.get('href',
                                                                                               None) is not None:
            new_links.append(url.get('href', None))
    # 随机拿一个
    print(new_links)
    url = new_links[random.randint(0, len(new_links) - 1)]
    redirect_url = originalLinkGetsRedirectUrl(url)
    # print("初始获取重定向后的链接：", redirect_url)
    while 'unsubscribe' in redirect_url:
        url = new_links[random.randint(0, len(new_links) - 1)]
        redirect_url = originalLinkGetsRedirectUrl(url)
    print("获取非退订包含utm链接：", originalLinkGetsRedirectUrl(url))
    return url


def originalLinkGetsRedirectUrl(url):
    """
    原始链接获取重定向后带有utm的链接
    @param url:
    @return:
    """
    global final_location_url
    print(url)
    try:
        session = requests.session()
        resp_1 = session.get(url, allow_redirects=True)
        # print("第一次重定向：",resp_1.headers.get('Location'))
        # location_url_1 = resp_1.headers.get('Location')
        # resp_2 = session.get(location_url_1, allow_redirects=False)
        # print("第二次重定向：",resp_2.headers.get('Location'))
        # final_location_url = resp_2.headers.get('Location')
        final_location_url = resp_1.url
        return final_location_url
    except:
        raise


def parseUrlParameters(url):
    """
    返回url后的拼接参数
    @param url:
    @return:
    """
    return parse_qs(requests.utils.urlparse(url).query)


def name_convert_to_snake(name: str) -> str:
    """驼峰转下划线"""
    if re.search(r'[^_][A-Z]', name):
        name = re.sub(r'([^_])([A-Z][a-z]+)', r'\1_\2', name)
        return name_convert_to_snake(name)
    return name.lower()


def assertUtmConfig(emailProperty):
    """
    断言utm
    @param utmConfigInfo: 请求时存的utm参数
    @param emailUtmConfig: 邮件内容获取的utm参数
    @param activityId:
    @return:
    """
    global EmailContentAll
    for _email in emailProperty:
        _subject = list(_email.keys())[0]
        try:
            UIDs = selectFolderGetUids(imapObj, allEmail, _subject)
            assert UIDs
            EmailContentAll = forParseEmailContent(UIDs, True)
        except AssertionError:
            UIDs = selectFolderGetUids(imapObj, junkEmail, _subject)
            assert UIDs
            EmailContentAll = forParseEmailContent(UIDs, True)
        except Exception as e:
            raise e
        finally:
            email = _email[_subject]
            if email['utmConfigInfo'] is None:
                print("--->测试邮件不进行utm校验")
                break
            temp = originalLinkGetsRedirectUrl(getRandomHyperlinksInHtml(EmailContentAll))
            params = parseUrlParameters(temp)
            for utmKey, utmValue in email['utmConfigInfo'].items():
                assert params.get(name_convert_to_snake(utmKey))[0] == utmValue
            # 断言sp参数
            # ec1
            if 'utm_term' in params:
                utm_term = dict(parse.parse_qsl(params.get('utm_term')[0]))
                _params = {**params, **utm_term}
                params = _params
                assert params.get('sp_medium') == 'email'
                assert params.get('sp_source') == 'smartpush'
                if email['activityId'] is not None:
                    assert params.get('sp_campaign') == str(email['activityId'])
            # ec2
            else:
                assert params.get('sp_medium')[0] == 'email'
                assert params.get('sp_source')[0] == 'smartpush'
                if email['activityId'] is not None:
                    assert params.get('sp_campaign')[0] == str(email['activityId'])
                # flow的断言需要另外写
            print(f"UTM断言成功-->>{email['utmConfigInfo']} || {params} || {str(email['activityId'])}")


@retry(tries=3, delay=3, backoff=3, max_delay=20)
def check_email_content(emailProperty, loginEmail, password, **kwargs):
    """
    校验邮件送达情况
    loginEmail: 接收邮箱账号，必填
    password: 邮箱密码，必填
    emailProperty: list类型，格式: [{主旨: {receiveAddress: 回复邮箱, sender: 发件人}}], 必填

    is_check_email_property: bool, 非必填，是否断言回复邮箱或发件人
    is_check_utm: bool, 非必填，是否断言utm
    """
    global imapObj
    try:
        print("--->获取emailProperty变量", emailProperty)
        imapObj = loginShowFoldersEmail(loginEmail, password)
        result = assertEmail(emailProperty=emailProperty, **kwargs)
        # assertUtmConfig(emailProperty)
        return result
    except Exception:
        raise Exception
    finally:
        # 退出登录
        imapObj.logout()
