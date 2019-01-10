from django.urls import path
from Search.view import views

urlpatterns = [
    path('', views.search),
    path('page/', views.index),
    path('page/search', views.page_search),
]
