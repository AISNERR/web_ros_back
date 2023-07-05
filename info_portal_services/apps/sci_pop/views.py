import datetime
from collections import OrderedDict

from django.utils.dateparse import parse_datetime
from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions, generics, status
from rest_framework.exceptions import ValidationError, ErrorDetail
from rest_framework.response import Response

from info_portal_services.generic.app_permissions import IsObjectOwnerOrAppAdmin, IsAppModeratorOrAdmin, IsAppAdmin
from .models import SciPop, StatusTypes, SciPopModeratorComments
from .serializers import SciPopGetSerializer, SciPopCreateSerializer, SciPopStatusSerializer, \
    SciPopModerationSerializer, SciPopCommentSerializer, ArchiveSciPopSerializer

from ..events.permissions import IsEventOwnerOrReadOnly, IsEventOwnerOrStaff


class SciPopListCreateAPIView(ListCreateAPIView):
    MAX_OBJECTS_NUM = 100
    queryset = SciPop.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SciPopGetSerializer
        return SciPopCreateSerializer

    def get_queryset(self):
        queryset = super(SciPopListCreateAPIView, self).get_queryset()\
            .filter(sci_pop_status__status="published")
        queryset = self.filtering_by_date(queryset)
        queryset = self.filtering_by_material_date(queryset)
        queryset = self.filtering_by_tags(queryset)
        queryset = self.filtering_by_format(queryset)
        queryset = self.filtering_by_author(queryset)
        queryset = self.filtering_by_subject(queryset)
        queryset = self.filtering_by_user(queryset)
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

    def filtering_by_user(self, queryset):
        f_user = self.request.query_params.getlist('user')
        if f_user:
            queryset = queryset.filter(created_by__username__in=f_user)
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

    def filtering_by_material_date(self, queryset):
        material_date = self.request.query_params.get('materialDateFrom')
        material_date_to = self.request.query_params.get('materialDateTo')
        if material_date:
            date_request = parse_datetime(material_date)
            if date_request:
                queryset = queryset.filter(material_date__gte=date_request)
        if material_date_to:
            date_request = parse_datetime(material_date_to)
            if date_request:
                if date_request.time() == datetime.time(0, 0, 0):
                    date_request += datetime.timedelta(days=1)
                queryset = queryset.filter(material_date__lte=date_request)
        return queryset

    def filtering_by_tags(self, queryset):
        f_tags = self.request.query_params.getlist('tag')
        if f_tags:
            try:
                queryset = queryset.filter(tags__in=f_tags).distinct()
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
        f_format = self.request.query_params.getlist('m_format')
        if f_format:
            try:
                queryset = queryset.filter(format__in=f_format).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_author(self, queryset):
        f_authors = self.request.query_params.getlist('author')
        if f_authors:
            try:
                queryset = queryset.filter(authors__full_name__in=f_authors).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def perform_create(self, serializer):
        authors = self.request.data.getlist('author')
        tags = self.request.data.getlist('tag')
        if not authors is None and len(authors):
            if "" in authors:
                raise ValidationError(OrderedDict([('author',
                                                    [ErrorDetail(string='Must be filled in.', code='required')])]))
        else:
            raise ValidationError(OrderedDict([('author', [ErrorDetail(string='This field is required.',
                                                                    code='required')])]))
        if not tags is None and len(tags):
            if "" in tags:
                raise ValidationError(OrderedDict([('tag',
                                                    [ErrorDetail(string='Must be filled in.', code='required')])]))
        else:
            raise ValidationError(OrderedDict([('tag', [ErrorDetail(string='This field is required.',
                                                                        code='required')])]))
        serializer.save(created_by=self.request.user, authors=authors, tags=tags)


class SciPopDetailAllAPIView(ListCreateAPIView):
    MAX_OBJECTS_NUM = 100

    queryset = SciPop.objects.all()
    serializer_class = SciPopGetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super(SciPopDetailAllAPIView, self).get_queryset()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if not ("app-moderator" in user_groups or "app-admin" in user_groups):
            queryset = queryset.filter(created_by=self.request.user)
        queryset = self.filtering_by_date(queryset)
        queryset = self.filtering_by_tags(queryset)
        queryset = self.filtering_by_format(queryset)
        queryset = self.filtering_by_author(queryset)
        queryset = self.filtering_by_material_date(queryset)
        queryset = self.filtering_by_subject(queryset)
        queryset = self.filtering_by_user(queryset)
        queryset = self.filtering_by_status(queryset)
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

    def filtering_by_status(self, queryset):
        f_status = self.request.query_params.getlist('status')
        if f_status:
            queryset = queryset.filter(sci_pop_status__in=f_status).order_by('sci_pop_status').distinct()
        return queryset

    def filtering_by_user(self, queryset):
        f_user = self.request.query_params.getlist('user')
        if f_user:
            queryset = queryset.filter(created_by__username__in=f_user).distinct()
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

    def filtering_by_material_date(self, queryset):
        material_date = self.request.query_params.get('materialDateFrom')
        material_date_to = self.request.query_params.get('materialDateTo')
        if material_date:
            date_request = parse_datetime(material_date)
            if date_request:
                queryset = queryset.filter(material_date__gte=date_request)
        if material_date_to:
            date_request = parse_datetime(material_date_to)
            if date_request:
                queryset = queryset.filter(material_date__lte=date_request)
        return queryset

    def filtering_by_tags(self, queryset):
        f_tags = self.request.query_params.getlist('tag')
        if f_tags:
            try:
                queryset = queryset.filter(tags__in=f_tags).distinct()
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
        f_format = self.request.query_params.getlist('m_format')
        if f_format:
            try:
                queryset = queryset.filter(format__in=f_format).distinct()
            except (TypeError, ValueError):
                pass
        return queryset

    def filtering_by_author(self, queryset):
        f_authors = self.request.query_params.getlist('author')
        if f_authors:
            try:
                queryset = queryset.filter(authors__full_name__in=f_authors).distinct()
            except (TypeError, ValueError):
                pass
        return queryset


class SciPopRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SciPop.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsEventOwnerOrReadOnly]
    http_method_names = ["get", "put", "delete"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SciPopGetSerializer
        return SciPopCreateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sci_pop_status.status != "published":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user_groups = [g.name for g in self.request.user.groups.all()]
        instance = self.get_object()
        if (instance.sci_pop_status.status not in ("created", "archived")) or (
            not "app-admin" in user_groups and instance.sci_pop_status.status == "archived"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        authors = self.request.data.getlist('author')
        tags = self.request.data.getlist('tag')
        if not authors is None and len(authors):
            if "" in authors:
                raise ValidationError(OrderedDict([('author',
                                                    [ErrorDetail(string='Must be filled in.', code='required')])]))
        else:
            raise ValidationError(OrderedDict([('author', [ErrorDetail(string='This field is required.',
                                                                        code='required')])]))
        if not tags is None and len(tags):
            if "" in tags:
                raise ValidationError(OrderedDict([('tag',
                                                    [ErrorDetail(string='Must be filled in.', code='required')])]))
        else:
            raise ValidationError(OrderedDict([('tag', [ErrorDetail(string='This field is required.',
                                                                     code='required')])]))
        serializer.save(created_by=self.request.user, authors=authors, tags=tags)

    def update(self, request, *args, **kwargs):
        allowed_statuses = (
            "created",
            "returned",
        )
        instance = self.get_object()
        if instance.sci_pop_status.status not in allowed_statuses:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(SciPopRUDAPIView, self).update(request, *args, **kwargs)


class SciPopDetailAPIView(generics.RetrieveAPIView):
    queryset = SciPop.objects.all()
    serializer_class = SciPopGetSerializer
    permission_classes = [IsEventOwnerOrStaff]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if ("app-moderator" in user_groups or "app-admin" in user_groups) and \
                instance.sci_pop_status.status == "ready_for_review":
            instance.sci_pop_status = StatusTypes.objects.get_or_create(status="review")[0]
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SciPopSendToReviewAPIView(generics.UpdateAPIView):
    queryset = SciPop.objects.all()
    serializer_class = SciPopStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsObjectOwnerOrAppAdmin]
    http_method_names = ["put"]

    def get_queryset(self):
        queryset = super(SciPopSendToReviewAPIView, self).get_queryset()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if "app-admin" in user_groups:
            return queryset
        return queryset.filter(created_by=self.request.user.id).filter(sci_pop_status__status="created")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sci_pop_status.status not in ("created", "returned"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        super(SciPopSendToReviewAPIView, self).update(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK, data={"status": 2})


class SciPopStatusModerationAPIView(generics.UpdateAPIView):
    queryset = SciPop.objects.all()
    serializer_class = SciPopModerationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]
    http_method_names = ["put"]

    def perform_update(self, serializer):
        published_at = datetime.datetime.now()
        serializer.save(created_by=self.request.user, published_at=published_at)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.sci_pop_status.status != "review":
        if instance.sci_pop_status.status not in ("review", "ready_for_review"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(SciPopStatusModerationAPIView, self).update(request, *args, **kwargs)


class SciPopCommentModerator(generics.ListCreateAPIView):
    queryset = SciPopModeratorComments.objects.all()
    serializer_class = SciPopCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]


class SciPopUpdateCommentModerator(generics.RetrieveUpdateDestroyAPIView):
    queryset = SciPopModeratorComments.objects.all()
    serializer_class = SciPopCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]
    http_method_names = ["get", "put", "delete"]


class ArchiveSciPopAPIView(generics.UpdateAPIView):
    queryset = SciPop.objects.all()
    serializer_class = ArchiveSciPopSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppAdmin]
    http_method_names = ["put"]
