import json
from datetime import timedelta

from django.utils.timezone import make_aware
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.utils.dateparse import parse_datetime

from info_portal_services.generic.app_permissions import IsAppModeratorOrAdmin, IsObjectOwnerOrAppAdmin, \
    IsAppAdmin
from .models import PostInGallery, GalleryModeratorComments
from .serializers import  GalleryCommentSerializer, \
    GalleryGetSerializer, GalleryCreateSerializer, GalleryInfoSerializer, GalleryStatusSerializer, \
    GalleryModerationSerializer, ArchiveGallerySerializer
from ..events.permissions import IsEventOwnerOrStaff, IsEventOwnerOrReadOnly
from ..status_model.models import StatusTypes


class GalleryListCreateAPIView(generics.ListCreateAPIView):
    queryset = PostInGallery.objects.all().filter(photo_gallery_status__status="published")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GalleryGetSerializer
        return GalleryCreateSerializer

    def perform_create(self, serializer):
        location = self.request.data.get('location')
        if isinstance(location, str):
            try:
                location = json.loads(location)
            except ValueError:
                raise ParseError(detail="Invalid location")
            serializer.save(created_by=self.request.user, location=location)
        else:
            raise ParseError(detail="No location provided")
    
    def get_queryset(self):
        queryset = super(GalleryListCreateAPIView, self).get_queryset()
        queryset = self.filtering_by_date(queryset)
        queryset = self.filtering_by_tags(queryset)
        queryset = self.filtering_by_subject(queryset)
        queryset = self.filtering_by_author(queryset)
        queryset = self.filtering_by_user(queryset)
        return queryset

    def filtering_by_user(self, queryset):
        f_user = self.request.query_params.get('user')
        if f_user:
            queryset = queryset.filter(created_by__username=f_user)
        return queryset

    def filtering_by_author(self, queryset):
        f_author = self.request.query_params.getlist('author')
        try:
            if f_author:
                queryset = queryset.filter(author__in=f_author).distinct()
        except (TypeError, ValueError):
            pass
        return queryset

    def filtering_by_tags(self, queryset):
        f_tag = self.request.query_params.getlist('tag')
        try:
            if f_tag:
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
                queryset = queryset.filter(created_at__lte=date_request)
        return queryset


class GalleryRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PostInGallery.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsEventOwnerOrReadOnly]
    http_method_names = ["get", "put", "delete"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GalleryGetSerializer
        return GalleryCreateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.photo_gallery_status.status != "published":
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user_groups = [g.name for g in self.request.user.groups.all()]
        instance = self.get_object()
        if (instance.photo_gallery_status.status not in ("created", "archived")) or (
                not "app-admin" in user_groups and instance.photo_gallery_status.status == "archived"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        allowed_statuses = (
            "created",
            "returned",
        )
        instance = self.get_object()
        if instance.photo_gallery_status.status not in allowed_statuses:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(GalleryRUDAPIView, self).update(request, *args, **kwargs)

    def perform_update(self, serializer):
        location = self.request.data.get('location')
        if isinstance(location, str):
            try:
                location = json.loads(location)
            except ValueError:
                raise ParseError(detail="Invalid location")
            serializer.save(created_by=self.request.user, location=location)
        else:
            raise ParseError(detail="No location provided")


class GalleryCommentModerator(generics.ListCreateAPIView):
    queryset = GalleryModeratorComments.objects.all()
    serializer_class = GalleryCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]


class GalleryUpdateCommentModerator(generics.RetrieveUpdateDestroyAPIView):
    queryset = GalleryModeratorComments.objects.all()
    serializer_class = GalleryCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]
    http_method_names = ["get", "put", "delete"]


class GalleryDetailAllAPIView(generics.ListAPIView):
    MAX_OBJECTS_NUM = 100

    queryset = PostInGallery.objects.all()
    serializer_class = GalleryInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super(GalleryDetailAllAPIView, self).get_queryset()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if not ("app-moderator" in user_groups or "app-admin" in user_groups):
            queryset = queryset.filter(created_by=self.request.user)
        queryset = self.filtering_by_date(queryset)
        queryset = self.filtering_by_tags(queryset)
        queryset = self.filtering_by_subject(queryset)
        queryset = self.filtering_by_author(queryset)
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
            queryset = queryset.filter(photo_gallery_status__in=f_status).order_by('photo_gallery_status').distinct()
        return queryset

    def filtering_by_user(self, queryset):
        f_user = self.request.query_params.get('user')
        if f_user:
            queryset = queryset.filter(created_by__username=f_user)
        return queryset

    def filtering_by_author(self, queryset):
        f_author = self.request.query_params.getlist('author')
        try:
            if f_author:
                queryset = queryset.filter(author__in=f_author).distinct()
        except (TypeError, ValueError):
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


class GalleryDetailAPIView(generics.RetrieveAPIView):
    queryset = PostInGallery.objects.all()
    serializer_class = GalleryInfoSerializer
    permission_classes = [IsEventOwnerOrStaff]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if ("app-moderator" in user_groups or "app-admin" in user_groups) and \
                instance.photo_gallery_status.status == "ready_for_review":
            instance.photo_gallery_status = StatusTypes.objects.get_or_create(status="review")[0]
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class GallerySendToReviewAPIView(generics.UpdateAPIView):
    queryset = PostInGallery.objects.all()
    serializer_class = GalleryStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsObjectOwnerOrAppAdmin]
    http_method_names = ["put"]

    def get_queryset(self):
        queryset = super(GallerySendToReviewAPIView, self).get_queryset()
        user_groups = [g.name for g in self.request.user.groups.all()]
        if "app-admin" in user_groups:
            return queryset
        return queryset.filter(created_by=self.request.user.id).filter(photo_gallery_status__status="created")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.photo_gallery_status.status not in ("created", "returned"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        super(GallerySendToReviewAPIView, self).update(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK, data={"status": 2})


class GalleryStatusModerationAPIView(generics.UpdateAPIView):
    queryset = PostInGallery.objects.all()
    serializer_class = GalleryModerationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.photo_gallery_status.status != "review":
        if instance.photo_gallery_status.status not in ("review", "ready_for_review"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(GalleryStatusModerationAPIView, self).update(request, *args, **kwargs)


class ArchiveGalleryAPIView(generics.UpdateAPIView):
    queryset = PostInGallery.objects.all()
    serializer_class = ArchiveGallerySerializer
    permission_classes = [permissions.IsAuthenticated, IsAppAdmin]
    http_method_names = ["put"]

