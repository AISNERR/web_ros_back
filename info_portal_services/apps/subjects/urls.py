from django.urls import path

from .views import *

urlpatterns = [
    path('subjects/', SubjectsListCreateAPIView.as_view(), name="subjects-list-create"),
    path('subjects/<int:pk>/', SubjectsRetrieveDestroyAPIView.as_view(), name="subjects-id-response"),
]
