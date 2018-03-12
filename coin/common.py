from django.shortcuts import render


def login_required(func):
    def wrapper(request, *args, **kw):
        username = request.session.get("username", default=None)
        if not username:
            return render(request, "error.html", {"errMsg": "未登录"})
        else:
            return func(request, *args, **kw)

    return wrapper
