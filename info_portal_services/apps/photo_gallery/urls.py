from django.urls import path

from .views import *


urlpatterns = [
    path('photo_gallery/', GalleryListCreateAPIView.as_view(), name="photo-gallery-list-create"),
    path('photo_gallery/detailed/', GalleryDetailAllAPIView.as_view(), name="photo-gallery-detailed"),
    path('photo_gallery/<int:pk>/', GalleryRUDAPIView.as_view(), name="photo-gallery-rud"),
    path('photo_gallery/<int:pk>/info/', GalleryDetailAPIView.as_view(), name="photo-gallery-info"),
    path('photo_gallery/<int:pk>/to_review/', GallerySendToReviewAPIView.as_view(), name="photo-gallery-send-to-review"),
    path('photo_gallery/<int:pk>/moderate/', GalleryStatusModerationAPIView.as_view(), name="photo-gallery-status-moderation"),
    path('photo_gallery/comments/', GalleryCommentModerator.as_view(), name="photo-gallery-admin-moderation"),
    path('photo_gallery/comments/<int:pk>/', GalleryUpdateCommentModerator.as_view(), name="photo-gallery-admin-moderation-update"),
    path('photo_gallery/archive/<int:pk>/', ArchiveGalleryAPIView.as_view(), name="photo-gallery-archive"),
]