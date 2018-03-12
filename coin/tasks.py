import threading
import logging
from coin import email


def startRealTimeThread():
    logging.info("startRealTimeThread================")

    # 开启发送邮件线程
    t = threading.Thread(target=email.sendRealTimeEmail, name='realtime')
    t.start()


def startDayReportThread():
    logging.info("startDayReportThread================")

    # 开启发送日报邮件
    t = threading.Thread(target=email.sendDayEmail, name='day')
    t.start()
