from django.urls import path

from .views import *

urlpatterns = [
    path('tags/', TagsListCreateAPIView.as_view(), name="tags-list-create"),
    path('tags/<int:pk>/', TagsRetrieveDestroyAPIView.as_view(), name="tags-id-response"),
]
