from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from datetime import timedelta, datetime

from coin.models import *


def sendList(request):
    """
    发送邮件，短信提醒配置
    :param request:
    :return:
    """
    sends = SendConfig.objects.all()
    return render(request, "config/sendList.html", {"sends": sends})


def sendUpdate(request):
    if request.method == "POST":
        userId = request.POST.get("id")
        buyPrice = request.POST.get("buyPrice")
        salePrice = request.POST.get("salePrice")
        SendConfig.objects.filter(id=userId).update(buyPrice=buyPrice, salePrice=salePrice)
        return HttpResponseRedirect("/config/send")
    else:
        sendId = request.GET.get("id", default=None)
        send = SendConfig.objects.get(id=sendId)
        return render(request, "config/sendEdit.html", {"send": send})


def price(request):
    """
    获取价格信息获取
    :param request:
    :return:
    """
    if request.method == "GET":
        priceType = request.GET.get("priceType", default=None)
        startPriceDate = request.GET.get("startPriceDate", default=None)
        endPriceDate = request.GET.get("endPriceDate", default=None)
    else:
        priceType = request.POST.get("priceType", default=None)
        startPriceDate = request.POST.get("startPriceDate", default=None)
        endPriceDate = request.POST.get("endPriceDate", default=None)

    if priceType is None:
        priceType = 1
    else:
        priceType = int(priceType)

    if startPriceDate is None:
        yes = datetime.now() - timedelta(days=1)
        startPriceDate = yes.strftime('%Y-%m-%d') + " 00:00"

    if endPriceDate is None:
        yes = datetime.now() - timedelta(days=1)
        endPriceDate = yes.strftime('%Y-%m-%d') + " 23:59"

    pds = PriceData.objects.filter(priceType=priceType,
                                   recordTime__range=(startPriceDate + ":00", endPriceDate + ":59"))

    if priceType == 1:
        title = u"买入价格汇率曲线图"
    else:
        title = u"卖出价格汇率曲线图"

    dateDatas = []
    priceDatas = []
    rateDatas = []
    if pds is not None and len(pds) > 0:
        for pd in pds:
            dateDatas.append(str(pd.recordTime)[:-3])
            priceDatas.append(float(pd.price))
            rateDatas.append(float(pd.rate))

    return render(request, "config/priceLineChart.html", {
        "startPriceDate": startPriceDate,
        "endPriceDate": endPriceDate,
        "chartTitle": title,
        "dateDatas": dateDatas,
        "priceDatas": priceDatas,
        "rateDatas": rateDatas
    })
