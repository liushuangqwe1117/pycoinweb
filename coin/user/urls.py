from django.urls import path, re_path

from . import views

urlpatterns = [
    # 通过别名，引用URL
    path('list/', views.userList, name="userListAlias"),
    # path('edit/', views.userEdit),
    # 使用restful模式，其中?P<userId>为标准格式，即匹配到的值传递给方法中userId参数
    # 如果无?P<userId>模式，则匹配的参数按照顺序传递给方法中的参数
    re_path('edit/(?P<userId>\d+)/', views.userEdit),
    # POST提交，URL必须完全匹配，包括最后的/，GET请求/可加可不加
    path('update/', views.userUpdate)

]
