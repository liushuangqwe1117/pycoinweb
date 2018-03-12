# -*- coding: utf-8 -*-

import urllib.request
import json
import time
import smtplib
import os
from datetime import timedelta, datetime
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import encoders
from django.template import loader
import logging
import xlsxwriter

from coin import constants
from coin.models import SystemConfig, PriceData, SendConfig


class EmailSystemConfig(object):
    def __init__(self):
        self.host = None
        self.user = None
        self.password = None

    def __str__(self):
        return "host=%s,user=%s,pass=%s" % (self.host, self.user, self.password)


class EmailEntity(object):
    def __init__(self):
        self.receivers = None
        self.subject = None
        self.content = None
        self.hasAttach = False
        self.filePath = None
        self.fileName = None

    def __str__(self):
        return ','.join(self.receivers)


class RealTimeData(object):
    def __init__(self):
        self.queryTime = None
        self.merchant = None
        self.price = None


emailSystemConfig = EmailSystemConfig()


def _getEmailSystemConfig():
    global emailSystemConfig

    configs = SystemConfig.objects.filter(module=SystemConfig.module_choice[0][0])
    emailSystemConfig = EmailSystemConfig()
    for cf in configs:
        if constants.EMAIL_HOST_KEY == cf.paramCode:
            emailSystemConfig.host = cf.paramValue
        if constants.EMAIL_USER_KEY == cf.paramCode:
            emailSystemConfig.user = cf.paramValue
        if constants.EMAIL_PASS_KEY == cf.paramCode:
            emailSystemConfig.password = cf.paramValue

    logging.info("获取邮件配置：%s" % emailSystemConfig)


def sendEMail(emailEntity):
    if emailSystemConfig.host is None:
        _getEmailSystemConfig()

    if emailEntity.hasAttach:
        message = MIMEMultipart()
        mailBody = MIMEText(emailEntity.content, 'plain', 'utf-8')
        message.attach(mailBody)

        part = MIMEBase('application', 'octet-stream')
        with open(emailEntity.filePath, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment; filename=' + emailEntity.fileName)
        message.attach(part)

        message['Subject'] = Header(emailEntity.subject, 'utf-8')
    else:
        message = MIMEText(emailEntity.content, 'html', 'utf-8')
        message['Subject'] = Header(emailEntity.subject, 'utf-8')

    message['From'] = "{}".format(emailSystemConfig.user)
    message['To'] = ",".join(emailEntity.receivers)

    try:
        # smtp=smtplib.SMTP()
        smtp = smtplib.SMTP_SSL(emailSystemConfig.host, 465, 'localhost')
        # smtp.connect(mail_host, 25)
        logging.info("连接服务器")
        smtp.login(emailSystemConfig.user, emailSystemConfig.password)
        logging.info("登录服务器")
        smtp.sendmail(emailSystemConfig.user, emailEntity.receivers, message.as_string())
        smtp.quit()
        logging.info("mail has been send successfully.")
    except smtplib.SMTPException as e:
        logging.info("email error:" + str(e))


def getData(url):
    headers = ("User-Agent", "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko")
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    # 将opener安装为全局
    urllib.request.install_opener(opener)
    data = urllib.request.urlopen(url).read().decode("utf-8", "ignore")

    text = json.loads(data)
    return text


def saveData(dataUrl, rateUrl, priceType):
    if not os.path.exists(constants.BASE_FILE_PATH):
        os.makedirs(constants.BASE_FILE_PATH)

    try:
        text = getData(dataUrl)
    except Exception as error:
        logging.error("获取火币价格数据失败：%s" % str(error))
        logging.exception(error)
        return

    try:
        rate = getData(rateUrl)
    except Exception as error:
        logging.error("获取汇率数据失败：%s" % str(error))
        logging.exception(error)
        return

    dataLen = len(rate['data'])
    rateVal = ""
    for j in range(0, dataLen):
        if rate['data'][j]['coinName'] == "USDT":
            rateVal = str(rate['data'][j]['price'])

    textData = text['data']
    # 以第三个商户的价格存入数据库
    merchant = textData[0]['userName']
    p3 = textData[2]['price']

    # 将数据存入数据库
    pd = {
        "merchantName": merchant,
        "price": p3,
        "rate": rateVal,
        "recordTime": time.strftime('%Y-%m-%d %H:%M:%S'),
        "coinType": 1,
        "priceType": priceType
    }
    rtn = PriceData.objects.create(**pd)
    return rtn, textData


class NowPrice(object):
    def __init__(self):
        self.price = None


def getEmailContent(title, textData, timeString):
    datas = []
    for i in range(0, 5):
        rtd = RealTimeData()
        rtd.queryTime = timeString
        rtd.merchant = textData[i]['userName']
        rtd.price = str(textData[i]['price'])
        datas.append(rtd)
    emailContent = loader.render_to_string("email/RealTimeTemplate.html", {"title": title, "datas": datas})
    return emailContent


def buySaleEmail(sendConfig, rtnData, nowPrice, isBuy):
    if rtnData is None:
        return

    priceData = rtnData[0]
    textData = rtnData[1]
    comparePrice = textData[0]['price']

    if isBuy and comparePrice > sendConfig.buyPrice:
        return

    if isBuy is False and comparePrice < sendConfig.salePrice:
        return

    # 准备邮件数据
    timeString = time.strftime('%Y-%m-%d %H:%M:%S')
    if isBuy:
        title = u"买入信息推送(USDT/CNY：" + priceData.rate + ")"
    else:
        title = u"卖出信息推送(USDT/CNY：" + priceData.rate + ")"

    emailContent = getEmailContent(title, textData, timeString)

    ee = EmailEntity()
    ee.receivers = [sendConfig.user.email]
    if isBuy:
        ee.subject = '[' + timeString + u']IN周末加班时间(USDT/CNY)'
    else:
        ee.subject = '[' + timeString + u']OUT周末聚会时间(USDT/CNY)'

    ee.content = emailContent
    ee.hasAttach = False

    if nowPrice.price is None:
        nowPrice.price = comparePrice
        sendEMail(ee)
        return

    if comparePrice != nowPrice.price:
        nowPrice.price = comparePrice
        sendEMail(ee)
        return


nowPriceDic = {}


def sendRealTimeEmail():
    logging.info("sendRealTimeEmail================")
    while True:
        # 一分钟爬取数据一次
        time.sleep(60)

        try:
            buyDataUrl = "https://api-otc.huobipro.com/v1/otc/trade/list/public?coinId=2&tradeType=1&currentPage=1&payWay=&country=&merchant=0&online=1&range=0"
            saleDataUrl = "https://api-otc.huobipro.com/v1/otc/trade/list/public?coinId=2&tradeType=0&currentPage=1&payWay=&country=&merchant=1&online=1&range=0"
            rateUrl = "https://api-otc.huobipro.com/v1/otc/base/market/price"
            buyData = saveData(buyDataUrl, rateUrl, 1)
            saleData = saveData(saleDataUrl, rateUrl, 2)

            sends = SendConfig.objects.all()
            if sends is not None and len(sends) > 0:
                for send in sends:
                    nowPrice = nowPriceDic.get(send.user.username)
                    if nowPrice is None:
                        nowPrice = NowPrice()
                        nowPriceDic[send.user.username] = nowPrice

                    # 买入
                    buySaleEmail(send, buyData, nowPrice, True)
                    # 卖出
                    buySaleEmail(send, saleData, nowPrice, False)
        except Exception as err:
            logging.exception(err)


# 记录发送邮件的日期
yesterday = None


def sendDayEmail():
    logging.info("sendDayEmail================")

    global yesterday

    # 通过循环来实现定时任务的效果
    while True:
        # 10分钟轮询一次
        time.sleep(600)

        if yesterday is None:
            yes = datetime.now() - timedelta(days=1)
            yesterday = yes.strftime('%Y-%m-%d')

        today = time.strftime('%Y-%m-%d')
        if today == yesterday:
            # 说明今天发送过邮件了
            return

        # 买入日报
        try:
            datas = PriceData.objects.filter(priceType=1,
                                             recordTime__range=(yesterday + " 00:00:00", yesterday + " 23:59:59"))
            if datas is not None and len(datas) > 0:
                logging.info(yesterday + u"买入日报数据量:" + str(len(datas)))
                sendDayFile(datas, True)
        except Exception as err:
            logging.exception(err)

        # 卖出日报
        try:
            datas = PriceData.objects.filter(priceType=2,
                                             recordTime__range=(yesterday + " 00:00:00", yesterday + " 23:59:59"))
            if datas is not None and len(datas) > 0:
                logging.info(yesterday + u"卖出日报数据量:" + str(len(datas)))
                sendDayFile(datas, False)
        except Exception as err:
            logging.exception(err)

        # 避免重复发送邮件
        yesterday = today


def sendDayFile(datas, isBuy):
    if isBuy:
        fileName = "buy-" + yesterday + ".xlsx"
    else:
        fileName = "sale-" + yesterday + ".xlsx"

    filePath = os.path.join(constants.BASE_FILE_PATH, fileName)
    logging.info("filePath：" + filePath)

    avgPrice = 0
    avgTotal = 0
    rateVal = 0

    # 打开最终写入的文件
    wb = xlsxwriter.Workbook(filePath)
    # 创建一个sheet工作对象
    ws = wb.add_worksheet()
    ws.write(0, 0, u"时间")
    ws.write(0, 1, u"价格")
    ws.write(0, 2, u"汇率")

    rowIndex = 1
    for data in datas:
        avgPrice += data.price
        avgTotal += 1
        rateVal = data.rate
        ws.write(rowIndex, 0, str(data.recordTime))
        ws.write(rowIndex, 1, data.price)
        ws.write(rowIndex, 2, data.rate)
        rowIndex += 1

    wb.close()

    # 发送邮件
    ap = avgPrice / avgTotal

    sends = SendConfig.objects.all()
    if sends is None or len(sends) == 0:
        return

    emails = []
    if sends is not None and len(sends) > 0:
        for send in sends:
            emails.append(send.user.email)

    ee = EmailEntity()
    ee.receivers = emails
    if isBuy:
        ee.subject = u'IN周末加班时间(USDT/CNY)(' + fileName + ')'
        ee.content = yesterday + u"平均买入价格(USDT/CNY：" + str(rateVal) + "):" + str(ap)
    else:
        ee.subject = u'OUT周末聚会时间(USDT/CNY)(' + fileName + ')'
        ee.content = yesterday + u"平均卖出价格(USDT/CNY：" + str(rateVal) + "):" + str(ap)

    ee.hasAttach = True
    ee.filePath = filePath
    ee.fileName = fileName
    sendEMail(ee)
