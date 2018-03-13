from django.urls import path

from . import views

urlpatterns = [
    path('send/', views.sendList),
    path('update/', views.sendUpdate),
    path('price/', views.price),
]
