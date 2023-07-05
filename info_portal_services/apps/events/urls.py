from django.urls import path

from .views import *


urlpatterns = [
    path('events/', EventsListCreateAPIView.as_view(), name="events-list-create"),
    path('events/detailed/', EventsDetailAllAPIView.as_view(), name="events-detailed"),
    path('events/<int:pk>/', EventsRUDAPIView.as_view(), name="events-rud"),
    path('events/<int:pk>/info/', EventsDetailAPIView.as_view(), name="events-info"),
    path('events/<int:pk>/to_review/', EventsSendToReviewAPIView.as_view(), name="events-send-to-review"),
    path('events/<int:pk>/moderate/', EventsStatusModerationAPIView.as_view(), name="events-status-moderation"),
    path('events/types/', EventTypesAPIView.as_view(), name="events-types"),
    path('events/types/<int:pk>/', EventTypesRUDAPIView.as_view(), name="events-types-id"),
    path('events/formats/', EventFormatsAPIView.as_view(), name="events-formats"),
    path('events/formats/<int:pk>/', EventFormatsRUDAPIView.as_view(), name="events-formats-id"),
    path('events/comments/', EventsCommentModerator.as_view(), name="events-admin-moderation"),
    path('events/comments/<int:pk>/', EventsUpdateCommentModerator.as_view(), name="events-admin-moderation-update"),
    path('events/archive/<int:pk>/', ArchiveEventAPIView.as_view(), name="events-archive"),
]
