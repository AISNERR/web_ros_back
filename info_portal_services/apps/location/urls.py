from django.urls import path

from .views import *

urlpatterns = [
    path('location/', LocationList.as_view(), name="locations-list-create"),
    path('location/<int:pk>/detailed/', LocationDetails.as_view(), name="locations-in-detailed"),
]