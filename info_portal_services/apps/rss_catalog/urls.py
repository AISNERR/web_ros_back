from django.urls import path

from .views import *

urlpatterns = [
    path('rss_sources/', NewsRssListCreateAPIView.as_view(), name="rss-sources"),
    path('rss_sources/<int:pk>/', NewsRssRUDAPIView.as_view(), name="rss-sources-id"),
    path('rss_sources_groups/', NewsRssGroupsListCreateAPIView.as_view(), name="rss-sources-groups"),
    path('rss_sources_groups/<int:pk>/', NewsRssGroupsRUDAPIView.as_view(), name="rss-sources-groups-id"),
]
