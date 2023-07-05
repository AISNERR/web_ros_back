from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from info_portal_services.generic.app_permissions import IsAppAdminOrReadOnly, IsAppAdmin
from .models import NewsRss, NewsRssGroups
from .serializers import NewsRssSerializer, NewsRssGroupsSerializer


class NewsRssListCreateAPIView(ListCreateAPIView):
    serializer_class = NewsRssSerializer
    queryset = NewsRss.objects.all()
    permission_classes = [IsAppAdminOrReadOnly]


class NewsRssRUDAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = NewsRssSerializer
    queryset = NewsRss.objects.all()
    permission_classes = [IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]


class NewsRssGroupsListCreateAPIView(ListCreateAPIView):
    serializer_class = NewsRssGroupsSerializer
    queryset = NewsRssGroups.objects.all()
    permission_classes = [IsAppAdmin]


class NewsRssGroupsRUDAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = NewsRssGroupsSerializer
    queryset = NewsRssGroups.objects.all()
    permission_classes = [IsAppAdmin]
    http_method_names = ["get", "put", "delete"]

