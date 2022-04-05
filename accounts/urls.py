
from django.contrib import admin
from django.urls import path
from . import views
app_name = "accounts"
urlpatterns = [
    path('idfinder/',views.idfinder,name='idfinder'),
    path('signin/',views.signin,name='signin'),
    path('signup/',views.signup,name='signup'),
    path('signout/',views.signout,name='signout'),
]
