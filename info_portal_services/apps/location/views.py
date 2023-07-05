from rest_framework import permissions, generics

from apps.location.models import Location
from apps.location.serializers import CreateLocationSerializer

class LocationList(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CreateLocationSerializer


class LocationDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CreateLocationSerializer