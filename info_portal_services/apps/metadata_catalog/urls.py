from django.urls import path

from .views import *


urlpatterns = [
    path('layers/', LayersListCreateAPIView.as_view(), name="layers"),
    path('layers/<int:pk>/', LayersRUDAPIView.as_view(), name="layers-id"),
    path('layers/groups/', LayerGroupsListCreateAPIView.as_view(), name="layers-groups"),
    path('layers/groups/<int:pk>/', LayerGroupsRUDAPIView.as_view(), name="layers-groups-id"),
    path('layers/types/', LayerTypesListCreateAPIView.as_view(), name="layers-types"),
    path('layers/types/<int:pk>/', LayerTypesRUDAPIView.as_view(), name="layers-types-id"),
    path('layers/services/', ServicesListCreateAPIView.as_view(), name="layers-services"),
    path('layers/services/<int:pk>/', ServicesRUDAPIView.as_view(), name="layers-services-id"),
    path('layers/viewset/', LayersViewSetListCreateAPIView.as_view(), name="layers-viewset"),
    path('layers/viewset/<int:pk>/', LayersViewSetRUDAPIView.as_view(), name="layers-viewset-id"),
]
