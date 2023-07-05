from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from info_portal_services.generic.app_permissions import IsAppAdminOrReadOnly
from .models import Tags
from .serializers import TagsSerializer


class TagsListCreateAPIView(ListCreateAPIView):
    serializer_class = TagsSerializer
    queryset = Tags.objects.all() 
    permission_classes = [IsAppAdminOrReadOnly]


class TagsRetrieveDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TagsSerializer
    queryset = Tags.objects.all() 
    permission_classes = [IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]
