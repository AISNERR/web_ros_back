from django.urls import path

from .views import *

urlpatterns = [
    path('sci_pub/', SciPubListCreateAPIView.as_view(), name="sci-pub-list-create"),
    path('sci_pub/<int:pk>/', SciPubRUDAPIView.as_view(), name="sci-pub-rud"),
    path('sci_pub/source/',  SourceListCreateAPIView.as_view(), name="source-list-create"),
    path('sci_pub/source/<int:pk>/',  SourceRUDAPIView.as_view(), name="source-rud"),
    path('sci_pub/pub_type/',  PubTypeListCreateAPIView.as_view(), name="pub-type-list-create"),
    path('sci_pub/pub_type/<int:pk>/',  PubTypeRUDAPIView.as_view(), name="pub-type-rud"),
    path('sci_pub/detailed/', SciPubDetailAllAPIView.as_view(), name="scipub-detailed"),
    path('sci_pub/<int:pk>/info/', SciPubDetailAPIView.as_view(), name="scipub-info"),
    path('sci_pub/<int:pk>/to_review/', SciPubSendToReviewAPIView.as_view(), name="scipub-send-to-review"),
    path('sci_pub/<int:pk>/moderate/', SciPubStatusModerationAPIView.as_view(), name="sci-pub-status-moderation"),
    path('sci_pub/comments/', SciPubCommentModerator.as_view(), name="sci-pub-admin-moderation"),
    path('sci_pub/comments/<int:pk>', SciPubUpdateCommentModerator.as_view(), name="sci-pub-admin-moderation-update"),
    path('sci_pub/archive/<int:pk>', ArchiveSciPubAPIView.as_view(), name="sci-pub-archive"),
]