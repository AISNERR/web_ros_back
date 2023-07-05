from django.urls import path

from .views import *

urlpatterns = [
    path('sci_pop/', SciPopListCreateAPIView.as_view(), name="sci-pop-list-create"),
    path('sci_pop/detailed/', SciPopDetailAllAPIView.as_view(), name="sci-pop-detailed"),
    path('sci_pop/<int:pk>/', SciPopRUDAPIView.as_view(), name="sci-pop-rud"),
    path('sci_pop/<int:pk>/info/', SciPopDetailAPIView.as_view(), name="sci-pop-info"),
    path('sci_pop/<int:pk>/to_review/', SciPopSendToReviewAPIView.as_view(), name="sci-pop-send-to-review"),
    path('sci_pop/<int:pk>/moderate/', SciPopStatusModerationAPIView.as_view(), name="sci-pop-status-moderation"),
    path('sci_pop/comments/', SciPopCommentModerator.as_view(), name="sci-pop-admin-moderation"),
    path('sci_pop/comments/<int:pk>/', SciPopUpdateCommentModerator.as_view(), name="sci-pop-admin-moderation-update"),
    path('sci_pop/archive/<int:pk>/', ArchiveSciPopAPIView.as_view(), name="sci-pop-archive")
]
