from rest_framework import routers
from django.urls import path

from api.views import CheckUser

router = routers.DefaultRouter()
app_name = 'api'


urlpatterns = [
    path('test_task/', CheckUser.as_view()),
]
