from django.http import HttpResponseRedirect
from django.shortcuts import render

from coin.models import User
from coin.common import login_required


@login_required
def userList(request):
    """
    获取用户列表
    :param request:
    :return:
    """
    users = User.objects.all()
    return render(request, "user/list.html", {"users": users})


@login_required
def userEdit(request):
    userId = request.GET.get("userId")
    user = User.objects.get(id=userId)
    return render(request, "user/edit.html", {"user": user})


@login_required
def userUpdate(request):
    userId = request.POST.get("id")
    email = request.POST.get("email")
    phone = request.POST.get("phone")
    User.objects.filter(id=userId).update(email=email, phone=phone)
    return HttpResponseRedirect("/user/list")
