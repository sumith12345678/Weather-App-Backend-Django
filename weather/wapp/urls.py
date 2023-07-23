from django.urls import path
from .views import *
urlpatterns = [
    path('reg/',UserRegister.as_view()),
    path('login/',UserLogin.as_view()),
    path('logout/',UserLogout.as_view()),
    path('weather/', SearchWeather.as_view())
]
