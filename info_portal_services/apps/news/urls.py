from django.urls import path

from .views import *


urlpatterns = [
    path('news/', NewsList.as_view(), name="news"),
    path('news/<int:pk>/', NewsDetail.as_view(), name="news-detail"),
    path('news/<int:pk>/status', NewsStatus.as_view(), name="news-status"),
    path('news/<int:pk>/review-comments/', NewsReviewCommentsView.as_view(), name="review-comments"),
    path('news/locations/', NewsLocationsList.as_view(), name="news-locations"),
    path('news/<int:pk>/location/', NewsLocationsDetails.as_view(), name="news-locations-detail"),
    path('news/reviews/', ReviewListCreate.as_view(), name="reviews"),
    path('news/reviews/<int:pk>', ReviewDetailsUpdateDelete.as_view(), name="reviews-detail"),
    path('news/reviews/<int:pk>/comments/', ReviewCommentsView.as_view()),
    path('news/statuses/', StatusTypesList.as_view(), name="statuses"),
]
