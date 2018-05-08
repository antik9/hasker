from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token

from . import views

app_name = 'api'

urlpatterns = [
    path('answers/', views.get_api_answers, name='get_answers'),
    path('api-token-auth/', obtain_jwt_token, name='obtain_token'),
    path('index/', views.get_api_index, name='index'),
    path('question/', views.get_api_question, name='get_question'),
    path('search/', views.get_api_search, name='search'),
    path('trending/', views.get_api_trending, name='trending'),
    re_path(r'.*', views.get_api_help, name='help'),
]
