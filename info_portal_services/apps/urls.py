from django.urls import include, path

urlpatterns = [
    path('', include('apps.events.urls')),
    path('', include('apps.news.urls')),
    path('', include('apps.tags.urls')),
    path('', include('apps.subjects.urls')),
    path('', include('apps.photo_gallery.urls')),
    path('', include('apps.rss_catalog.urls')),
    path('', include('apps.location.urls')),
    path('', include('apps.sci_pub.urls')),
    path('', include('apps.metadata_catalog.urls')),
    path('', include('apps.projects.urls')),
    path('', include('apps.sci_pop.urls')),
]
