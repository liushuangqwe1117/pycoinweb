from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .forms import LoginForm
from .models import *
from .common import login_required

__all__ = ('login', 'index', 'logout')


# Create your views here.


def login(request):
    if request.method == "POST":
        loginData = LoginForm(request.POST)

        if loginData.is_valid():
            uname = loginData.data["username"]
            pwd = loginData.data["password"]
            user = User.objects.filter(username=uname, password=pwd)
            if not user:
                return render(request, "error.html", {"errMsg": "登录失败"})
            else:
                request.session['username'] = uname
                # 校验通过
                return HttpResponseRedirect("/index/")
    else:
        username = request.session.get("username", default=None)
        if username:
            # 如果用户SESSION没有失效，则直接跳转到首页
            return HttpResponseRedirect("/index/")
        loginData = LoginForm()

    return render(request, "login.html", {"loginData": loginData})


@login_required
def index(request):
    users = User.objects.all()
    return render(request, "index.html", {"users": users})


@login_required
def logout(request):
    username = request.session.get("username", default=None)
    if username:
        del request.session["username"]  # 不存在时报错
    return HttpResponseRedirect("/")
