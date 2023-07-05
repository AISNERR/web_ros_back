from collections import OrderedDict
import datetime
from django.http import Http404

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, ErrorDetail
from django.utils.dateparse import parse_datetime

from .permissions import IsSciPubOwnerOrStaff
from .models import Source, PubType, SciPub, SciPubModeratorComments
from apps.status_model.models import StatusTypes
from info_portal_services.generic.app_permissions import IsObjectOwnerOrAppAdmin, IsAppModeratorOrAdmin, IsAppAdmin, IsAppAdminOrReadOnly
from .serializers import SciPubSourceSerializer, SciPubTypeSerializer, SciPubCreateSerializer, SciPubGetSerializer, \
    SciPubInfoSerializer, SciPubStatusSerializer, SciPubModerationSerializer, SciPubCommentSerializer, \
    ArchiveSciPubSerializer


class SourceListCreateAPIView(ListCreateAPIView):
    queryset = Source.objects.all()
    serializer_class = SciPubSourceSerializer
    permission_classes = [IsAppAdminOrReadOnly]


class SourceRUDAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Source.objects.all()
    serializer_class = SciPubSourceSerializer
    permission_classes = [IsAppAdminOrReadOnly]


class PubTypeListCreateAPIView(ListCreateAPIView):
    queryset = PubType.objects.all()
    serializer_class = SciPubTypeSerializer
    permission_classes = [IsAppAdminOrReadOnly]


class PubTypeRUDAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PubType.objects.all()
    serializer_class = SciPubTypeSerializer
    permission_classes = [IsAppAdminOrReadOnly]


class SciPubListCreateAPIView(ListCreateAPIView):
    queryset = SciPub.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SciPubGetSerializer
        return SciPubCreateSerializer

    def perform_create(self, serializer):
        authors = self.request.data.get('authors')
        if isinstance(authors, str):
            if not len(authors.strip()):
                raise ValidationError(OrderedDict([('authors',
                                                    [ErrorDetail(string='Must be filled in.', code='required')])]))
            authors = authors.split(',')
            serializer.save(created_by=self.request.user, authors=authors)
        else:
            raise ValidationError(OrderedDict([('authors', [ErrorDetail(string='This field is required.',
                                                                        code='required')])]))

    def get_queryset(self):
        queryset = SciPub.objects.all()
        queryset = self.filtering_by_tags(queryset)
        queryset = self.filtering_by_source(queryset)
        queryset = self.filtering_by_subject(queryset)
        queryset = self.filtering_by_type(queryset)
        queryset = self.filtering_by_authors(queryset)
        queryset = self.filtering_by_date(queryset)
        queryset = self.filtering_by_date_source(queryset)
        return queryset

    def filtering_by_source(self, queryset):
        f_source = self.request.query_params.getlist('source')
        if f_source:
            try:
                queryset = queryset.filter(scipub_source__in=f_source).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_authors(self, queryset):
        f_author = self.request.query_params.getlist('author')
        if f_author:
            try:
                queryset = queryset.filter(authors__in=f_author).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_type(self, queryset):
        f_type = self.request.query_params.getlist('type')
        if f_type:
            try:
                queryset = queryset.filter(scipub_type__in=f_type).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_date(self, queryset):
        date_query = self.request.query_params.get('createdFrom')
        date_query_to = self.request.query_params.get('createdTo')
        if date_query:
            date_request = parse_datetime(date_query)
            if date_request:
                queryset = queryset.filter(created_at__gte=date_request)
        if date_query_to:
            date_request = parse_datetime(date_query_to)
            if date_request:
                if date_request.time() == datetime.time(0, 0, 0):
                    date_request += datetime.timedelta(days=1)
                queryset = queryset.filter(created_at__lte=date_request)
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

    def filtering_by_date_source(self, queryset):
        src = self.request.query_params.getlist('data')
        if src:
            try:
                queryset = queryset.filter(source_date__in=src).distinct()
            except (TypeError, ValueError):
                raise Http404
        return queryset


class SciPubDetailAllAPIView(generics.ListAPIView):
    queryset = SciPub.objects.all()
    serializer_class = SciPubInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SciPub.objects.all()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if not ("app-moderator" in user_groups or "app-admin" in user_groups):
            queryset = queryset.filter(created_by=self.request.user)
        queryset = self.filtering_by_tags(queryset)
        queryset = self.filtering_by_source(queryset)
        queryset = self.filtering_by_subject(queryset)
        queryset = self.filtering_by_type(queryset)
        queryset = self.filtering_by_authors(queryset)
        queryset = self.filtering_by_date(queryset)
        queryset = self.filtering_by_status(queryset)
        queryset = self.filtering_by_date_source(queryset)
        return queryset

    def filtering_by_source(self, queryset):
        f_source = self.request.query_params.getlist('source')
        if f_source:
            try:
                queryset = queryset.filter(scipub_source__in=f_source).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_authors(self, queryset):
        f_author = self.request.query_params.getlist('author')
        if f_author:
            try:
                queryset = queryset.filter(authors__in=f_author).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_type(self, queryset):
        f_type = self.request.query_params.getlist('type')
        if f_type:
            try:
                queryset = queryset.filter(scipub_type__in=f_type).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_date(self, queryset):
        date_query = self.request.query_params.get('createdFrom')
        date_query_to = self.request.query_params.get('createdTo')
        if date_query:
            date_request = parse_datetime(date_query)
            if date_request:
                queryset = queryset.filter(created_at__gte=date_request)
        if date_query_to:
            date_request = parse_datetime(date_query_to)
            if date_request:
                if date_request.time() == datetime.time(0, 0, 0):
                    date_request += datetime.timedelta(days=1)
                queryset = queryset.filter(created_at__lte=date_request)
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

    def filtering_by_status(self, queryset):
        status_id = self.request.query_params.getlist('status')
        if status_id:
            try:
                queryset = queryset.filter(scipub_status__in=status_id).distinct()
            except (TypeError, ValueError):
                raise Http404
        return queryset

    def filtering_by_date_source(self, queryset):
        src = self.request.query_params.getlist('data')
        if src:
            try:
                queryset = queryset.filter(source_date__in=src).distinct()
            except (TypeError, ValueError):
                raise Http404
        return queryset


class SciPubRUDAPIView(RetrieveUpdateDestroyAPIView):
    queryset = SciPub.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSciPubOwnerOrStaff]
    http_method_names = ["get", "put", "delete"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SciPubGetSerializer
        return SciPubCreateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sci_pub_status.status != "published":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.scipub_status.status != "created":
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        allowed_statuses = (
            "created",
            "returned",
        )
        instance = self.get_object()
        if instance.scipub_status.status not in allowed_statuses:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(SciPubRUDAPIView, self).update(request, *args, **kwargs)


class SciPubDetailAPIView(generics.RetrieveAPIView):
    queryset = SciPub.objects.all()
    serializer_class = SciPubInfoSerializer
    permission_classes = [permissions.IsAuthenticated, IsSciPubOwnerOrStaff]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if ("app-moderator" in user_groups or "app-admin" in user_groups) and \
                instance.scipub_status.status == "ready_for_review":
            instance.scipub_status = StatusTypes.objects.get_or_create(status="review")[0]
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SciPubSendToReviewAPIView(generics.UpdateAPIView):
    queryset = SciPub.objects.all()
    serializer_class = SciPubStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsObjectOwnerOrAppAdmin]
    http_method_names = ["put"]

    def get_queryset(self):
        queryset = super(SciPubSendToReviewAPIView, self).get_queryset()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if "app-admin" in user_groups:
            return queryset
        return queryset.filter(created_by=self.request.user.id).filter(scipub_status__status="created")

    def update(self, request, *args, **kwargs):
        super(SciPubSendToReviewAPIView, self).update(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK, data={"status": 2})


class SciPubStatusModerationAPIView(generics.UpdateAPIView):
    queryset = SciPub.objects.all()
    serializer_class = SciPubModerationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.scipub_status.status != "review":
        if instance.scipub_status.status not in ("review", "ready_for_review"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(SciPubStatusModerationAPIView, self).update(request, *args, **kwargs)


class SciPubCommentModerator(generics.ListCreateAPIView):
    queryset = SciPubModeratorComments.objects.all()
    serializer_class = SciPubCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]


class SciPubUpdateCommentModerator(generics.RetrieveUpdateDestroyAPIView):
    queryset = SciPubModeratorComments.objects.all()
    serializer_class =SciPubCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]
    http_method_names = ["get", "put", "delete"]


class ArchiveSciPubAPIView(generics.UpdateAPIView):
    queryset = SciPub.objects.all()
    serializer_class = ArchiveSciPubSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppAdmin]
    http_method_names = ["put"]