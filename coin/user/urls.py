from django.urls import path

from . import views

urlpatterns = [
    # 通过别名，引用URL
    path('list/', views.userList, name="userListAlias"),
    path('edit/', views.userEdit),
    # POST提交，URL必须完全匹配，包括最后的/，GET请求/可加可不加
    path('update/', views.userUpdate)
]
