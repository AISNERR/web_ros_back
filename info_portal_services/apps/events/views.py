from datetime import timedelta
 
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from apps.status_model.models import StatusTypes

from info_portal_services.generic.app_permissions import IsObjectOwnerOrAppAdmin, IsAppModeratorOrAdmin, \
    IsAppAdminOrReadOnly, IsAppAdmin
from .models import Events, EventModeratorComments, EventFormats, EventTypes
from .permissions import IsEventOwnerOrReadOnly, IsEventOwnerOrStaff
from .serializers import EventsGetSerializer, EventsCreateSerializer, EventInfoSerializer, \
    EventsStatusSerializer, EventFormatsSerializer, EventTypesSerializer, EventsModerationSerializer, \
    EventsCommentSerializer, ArchiveEventSerializer


class EventsListCreateAPIView(generics.ListCreateAPIView):
    MAX_OBJECTS_NUM = 100

    queryset = Events.objects.all().filter(event_status__status="published")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EventsGetSerializer
        return EventsCreateSerializer

    def get_queryset(self):
        queryset = super(EventsListCreateAPIView, self).get_queryset()
        queryset = self.filtering_by_date(queryset)
        queryset = self.filtering_by_tags(queryset)
        queryset = self.filtering_by_author(queryset)
        queryset = self.filtering_by_subject(queryset)
        queryset = self.filtering_by_format(queryset)
        queryset = self.filtering_by_type(queryset)
        queryset = self.paging(queryset)
        return queryset[:self.MAX_OBJECTS_NUM]

    def paging(self, queryset):
        DEFAULT_OFFSET = 0
        DEFAULT_LIMIT = 30

        limit = self.request.query_params.get('limit', DEFAULT_LIMIT)
        offset = self.request.query_params.get('offset', DEFAULT_OFFSET)

        try:
            limit = int(limit)
            offset = int(offset)
            queryset = queryset.all()[offset:offset+limit]
        except ValueError:
            pass

        return queryset

    def filtering_by_date(self, queryset):
        date_query = self.request.query_params.get('date_start')
        date_query_to = self.request.query_params.get('date_end')
        if date_query:
            date_request_from = make_aware(parse_datetime(date_query))
            if date_request_from:
                queryset = queryset.filter(date_start__gte=date_request_from)
        if date_query_to:
            date_request_to = make_aware(parse_datetime(date_query_to)) + timedelta(hours=23)
            if date_query and date_request_to:
                date_request_from = make_aware(parse_datetime(date_query))
                queryset = queryset.filter(date_end__range=[date_request_from, date_request_to])
            elif date_request_to:
                queryset = queryset.filter(date_end__lte=date_request_to)
        return queryset

    def filtering_by_author(self, queryset):
        username = self.request.query_params.get('author')
        if username:
            queryset = queryset.filter(created_by__username=username)
        return queryset

    def filtering_by_tags(self, queryset):
        f_tag = self.request.query_params.getlist('tag')
        if f_tag:
            try:
                queryset = queryset.filter(tags__in=f_tag).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_subject(self, queryset):
        f_subject = self.request.query_params.getlist('subject')
        if f_subject:
            try:
                queryset = queryset.filter(subject__in=f_subject).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_format(self, queryset):
        f_format = self.request.query_params.getlist('event_format')
        if f_format:
            try:
                queryset = queryset.filter(event_format__in=f_format).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_type(self, queryset):
        f_type = self.request.query_params.getlist('event_type')
        if f_type:
            try:
                queryset = queryset.filter(event_type__in=f_type).distinct()
            except (TypeError, ValueError):
                pass
        return queryset


class EventsDetailAllAPIView(generics.ListAPIView):
    MAX_OBJECTS_NUM = 100

    queryset = Events.objects.all()
    serializer_class = EventInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super(EventsDetailAllAPIView, self).get_queryset()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if not ("app-moderator" in user_groups or "app-admin" in user_groups):
            queryset = queryset.filter(created_by=self.request.user)
        queryset = self.filtering_by_date(queryset)
        queryset = self.filtering_by_tags(queryset)
        queryset = self.filtering_by_author(queryset)
        queryset = self.filtering_by_subject(queryset)
        queryset = self.filtering_by_status(queryset)
        queryset = self.filtering_by_format(queryset)
        queryset = self.filtering_by_type(queryset)
        queryset = self.paging(queryset)
        return queryset[:self.MAX_OBJECTS_NUM]

    def filtering_by_status(self, queryset):
        status_id = self.request.query_params.getlist('event_status')
        if status_id:
            try:
                queryset = queryset.filter(event_status__in=status_id).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_author(self, queryset):
        username = self.request.query_params.get('author')
        if username:
            queryset = queryset.filter(created_by__username=username)
        return queryset

    def paging(self, queryset):
        DEFAULT_OFFSET = 0
        DEFAULT_LIMIT = 30

        limit = self.request.query_params.get('limit', DEFAULT_LIMIT)
        offset = self.request.query_params.get('offset', DEFAULT_OFFSET)

        try:
            limit = int(limit)
            offset = int(offset)
            queryset = queryset.all()[offset:offset+limit]
        except ValueError:
            pass

        return queryset

    def filtering_by_date(self, queryset):
        date_query = self.request.query_params.get('date_startFrom')
        date_query_to = self.request.query_params.get('date_endTo')
        if date_query:
            date_request_from = make_aware(parse_datetime(date_query))
            if date_request_from:
                queryset = queryset.filter(date_start__gte=date_request_from)
        if date_query_to:
            date_request_to = make_aware(parse_datetime(date_query_to)) + timedelta(hours=23)
            if date_query and date_request_to:
                date_request_from = make_aware(parse_datetime(date_query))
                queryset = queryset.filter(date_end__range=[date_request_from, date_request_to])
            elif date_request_to:
                queryset = queryset.filter(date_end__lte=date_request_to)
        return queryset

    def filtering_by_tags(self, queryset):
        f_tag = self.request.query_params.getlist('tag')
        if f_tag:
            try:
                queryset = queryset.filter(tags__in=f_tag).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_subject(self, queryset):
        f_subject = self.request.query_params.getlist('subject')
        if f_subject:
            try:
                queryset = queryset.filter(subject__in=f_subject).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_format(self, queryset):
        f_format = self.request.query_params.getlist('event_format')
        if f_format:
            try:
                queryset = queryset.filter(event_format__in=f_format).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_type(self, queryset):
        f_type = self.request.query_params.getlist('event_type')
        if f_type:
            try:
                queryset = queryset.filter(event_type__in=f_type).distinct()
            except (TypeError, ValueError):
                pass
        return queryset


class EventsDetailAPIView(generics.RetrieveAPIView):
    queryset = Events.objects.all()
    serializer_class = EventInfoSerializer
    permission_classes = [IsEventOwnerOrStaff]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if ("app-moderator" in user_groups or "app-admin" in user_groups) and \
                instance.event_status.status == "ready_for_review":
            instance.event_status = StatusTypes.objects.get_or_create(status="review")[0]
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class EventsRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Events.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsEventOwnerOrReadOnly]
    http_method_names = ["get", "put", "delete"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EventsGetSerializer
        return EventsCreateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.event_status.status != "published":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user_groups = [g.name for g in self.request.user.groups.all()]
        instance = self.get_object()
        if (instance.event_status.status not in ("created", "archived")) or (
            not "app-admin" in user_groups and instance.event_status.status == "archived"):
            return Response(status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        allowed_statuses = (
            "created",
            "returned",
        )
        instance = self.get_object()
        if instance.event_status.status not in allowed_statuses:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(EventsRUDAPIView, self).update(request, *args, **kwargs)


class EventsSendToReviewAPIView(generics.UpdateAPIView):
    queryset = Events.objects.all()
    serializer_class = EventsStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsObjectOwnerOrAppAdmin]
    http_method_names = ["put"]

    def get_queryset(self):
        queryset = super(EventsSendToReviewAPIView, self).get_queryset()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if "app-admin" in user_groups:
            return queryset
        return queryset.filter(created_by=self.request.user.id).filter(event_status__status="created")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.event_status.status not in ("created", "returned"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        super(EventsSendToReviewAPIView, self).update(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK, data={"status": 2})


class EventsStatusModerationAPIView(generics.UpdateAPIView):
    queryset = Events.objects.all()
    serializer_class = EventsModerationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.event_status.status != "review":
        if instance.event_status.status not in ("review", "ready_for_review"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(EventsStatusModerationAPIView, self).update(request, *args, **kwargs)


class EventsCommentModerator(generics.ListCreateAPIView):
    queryset = EventModeratorComments.objects.all()
    serializer_class = EventsCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]


class EventsUpdateCommentModerator(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventModeratorComments.objects.all()
    serializer_class = EventsCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]
    http_method_names = ["get", "put", "delete"]

   
class EventFormatsAPIView(generics.ListCreateAPIView):
    queryset = EventFormats.objects.all()
    serializer_class = EventFormatsSerializer
    permission_classes = [IsAppAdminOrReadOnly]


class EventFormatsRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventFormats.objects.all()
    serializer_class = EventFormatsSerializer
    permission_classes = [IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]


class EventTypesAPIView(generics.ListCreateAPIView):
    queryset = EventTypes.objects.all()
    serializer_class = EventTypesSerializer
    permission_classes = [IsAppAdminOrReadOnly]


class EventTypesRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventTypes.objects.all()
    serializer_class = EventTypesSerializer
    permission_classes = [IsAppAdminOrReadOnly]
    http_method_names = ["get", "put", "delete"]


class ArchiveEventAPIView(generics.UpdateAPIView):
    queryset = Events.objects.all()
    serializer_class = ArchiveEventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppAdmin]
    http_method_names = ["put"]
