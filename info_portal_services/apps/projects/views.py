from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Project, ProjectItem, ProjectTypes
from .serializers import ProjectSerializer, ProjectItemSerializer, \
    ProjectTypesSerializer


class ProjectTypesListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = ProjectTypesSerializer
    queryset = ProjectTypes.objects.all()
    permission_classes = [permissions.IsAuthenticated]

class ProjectsListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ProjectsRUDAPIView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ProjectItemsListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = ProjectItemSerializer
    queryset = ProjectItem.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ProjectItemsRUDAPIView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ProjectItemSerializer
    queryset = ProjectItem.objects.all()
    permission_classes = [permissions.IsAuthenticated]


