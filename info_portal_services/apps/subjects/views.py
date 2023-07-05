from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Subjects
from .serializers import SubjectsSerializer
from info_portal_services.generic.app_permissions import IsAppAdminOrReadOnly


class SubjectsListCreateAPIView(ListCreateAPIView):
    serializer_class = SubjectsSerializer
    queryset = Subjects.objects.all() 
    permission_classes = [IsAppAdminOrReadOnly]


class SubjectsRetrieveDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = SubjectsSerializer
    queryset = Subjects.objects.all() 
    permission_classes = [IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]
