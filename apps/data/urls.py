from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

# router.register('start-mailing', views.StartMailingView, basename='start_mailing')

urlpatterns = [
    path('file/', views.DBDataUpdateView.as_view()),
]

urlpatterns += router.urls
