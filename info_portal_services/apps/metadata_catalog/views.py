from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, status
from rest_framework.response import Response

from info_portal_services.generic.app_permissions import IsAppAdminOrReadOnly
from .models import Layers, LayerGroups, LayerTypes, Services, LayersViewSet
from .serializers import LayersSerializer, LayerGetSerializer, LayerGroupsSerializer, LayerTypesSerializer, \
    ServicesSerializer, LayersViewSetCreateSerializer, LayersViewSetGetSerializer


class LayerGroupsListCreateAPIView(ListCreateAPIView):
    serializer_class = LayerGroupsSerializer
    queryset = LayerGroups.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]


class LayerGroupsRUDAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = LayerGroupsSerializer
    queryset = LayerGroups.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]


class LayerTypesListCreateAPIView(ListCreateAPIView):
    serializer_class = LayerTypesSerializer
    queryset = LayerTypes.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]


class LayerTypesRUDAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = LayerTypesSerializer
    queryset = LayerTypes.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]


class ServicesListCreateAPIView(ListCreateAPIView):
    serializer_class = ServicesSerializer
    queryset = Services.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]


class ServicesRUDAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ServicesSerializer
    queryset = Services.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]


class LayersListCreateAPIView(ListCreateAPIView):
    queryset = Layers.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LayerGetSerializer
        return LayersSerializer

    def get_queryset(self):
        queryset = super(LayersListCreateAPIView, self).get_queryset()
        queryset = self.filtering_by_group(queryset)
        queryset = self.filtering_by_service(queryset)
        queryset = self.filtering_by_type(queryset)
        return queryset

    def filtering_by_group(self, queryset):
        f_layer_group = self.request.query_params.getlist('layer_group')
        if f_layer_group:
            try:
                queryset = queryset.filter(layer_group_id__in=f_layer_group).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_service(self, queryset):
        f_service = self.request.query_params.getlist('service')
        if f_service:
            try:
                queryset = queryset.filter(service_id__in=f_service).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_type(self, queryset):
        f_layer_type = self.request.query_params.getlist('layer_type')
        if f_layer_type:
            try:
                queryset = queryset.filter(layer_type_id__in=f_layer_type).distinct()
            except (TypeError, ValueError):
                pass
        return queryset


class LayersRUDAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Layers.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LayerGetSerializer
        return LayersSerializer


class LayersViewSetListCreateAPIView(ListCreateAPIView):
    queryset = LayersViewSet.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LayersViewSetGetSerializer
        return LayersViewSetCreateSerializer


class LayersViewSetRUDAPIView(RetrieveUpdateDestroyAPIView):
    queryset = LayersViewSet.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LayersViewSetGetSerializer
        return LayersViewSetCreateSerializer

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if LayersViewSet.objects.get(pk=pk).name == "root":
            layers = Layers.objects.all()
            serializer = LayerGetSerializer(data=layers, many=True)
            serializer.is_valid()
            return Response(serializer.data)
        return super(LayersViewSetRUDAPIView, self).get(request, *args, **kwargs)