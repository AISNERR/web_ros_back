import datetime

from rest_framework import permissions, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ParseError
from django.http import Http404
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from drf_yasg.utils import swagger_auto_schema

from .models import News, PubReviews,\
    ReviewComments, NewsReviewComments
from apps.location.models import Location
from apps.status_model.models import StatusTypes
from .serializers import NewsSerializer, NewsGetSerializer, \
    NewsUpdateStatusSerializer, PubReviewGetSerializer, PubReviewUpdateSerializer, \
    PubReviewCommentsSerializer, LocationSerializer, NewsGetListSerializer, \
    PubStatusSerializer, PubReviewCreateSerializer, NewsReviewCommentsSerializer
from .permissions import IsOwnerAndReadOnly, NewsDetailsPermissions
from info_portal_services.generic.app_permissions import IsAppModeratorOrAdmin
from .utils import validate_location


class NewsList(generics.ListCreateAPIView):
    MAX_OBJECTS_NUM = 100

    queryset = News.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        status = StatusTypes.objects.get(status='created')
        location = validate_location(self.request.data.get('location'))

        if location:
            serializer.save(created_by=self.request.user, location=location, status=status)
        else:
            serializer.save(created_by=self.request.user, status=status)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NewsGetListSerializer
        return NewsSerializer

    def get_queryset(self):
        queryset = News.objects.all()
        queryset = self.filtering_by_date(queryset)
        queryset = self.filtering_by_author(queryset)
        queryset = self.finding_bytags(queryset)
        queryset = self.finding_bysubject(queryset)
        queryset = self.filtering_by_status(queryset)
        queryset = self.filtering_by_permission(queryset)
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
            queryset = queryset.all()[offset:offset + limit]
        except ValueError:
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

    def filtering_by_author(self, queryset):
        username = self.request.query_params.get('author')
        if username:
            queryset = queryset.filter(created_by__username=username)
        return queryset

    def finding_bytags(self, queryset):
        f_tag = self.request.query_params.getlist('tag')
        try:
            if f_tag:
                queryset = queryset.filter(tags__in=f_tag).distinct()
        except (TypeError, ValueError):
            pass
        return queryset

    def finding_bysubject(self, queryset):
        f_subject = self.request.query_params.get('subject')
        if f_subject:
            queryset = queryset.filter(subject=f_subject)
        return queryset

    def filtering_by_status(self, queryset):
        status_id = self.request.query_params.getlist('status')
        if status_id:
            try:
                queryset = queryset.filter(status__in=status_id).distinct()
            except (TypeError, ValueError):
                raise Http404
        return queryset

    def filtering_by_permission(self, queryset):
        is_admin_user = self.is_admin_user()

        if self.request.user.is_authenticated:
            if not is_admin_user:
                queryset = queryset.filter(Q(created_by=self.request.user) | Q(status__id=7))
        else:
            queryset = queryset.filter(status__id=7)
        return queryset

    def is_admin_user(self):
        try:
            user_groups = [g.name for g in self.request.user.groups.all()]
            if "app-moderator" in user_groups or "app-admin" in user_groups:
                return True
        except AttributeError:
            pass
        return False


class NewsLocationsList(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = LocationSerializer

    def get_queryset(self):
        queryset = super(NewsLocationsList, self).get_queryset()
        try:
            user_groups = [g.name for g in self.request.user.groups.all()]
            if "app-moderator" in user_groups or "app-admin" in user_groups:
                return queryset
            else:
                try:
                    queryset = queryset.filter(
                        news_in_location__status=StatusTypes.objects.get_or_create(status="published")[0]
                    )
                except (TypeError, ValueError):
                    raise Http404
                return queryset
        except AttributeError:
            pass
    

class NewsLocationsDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = LocationSerializer
    http_method_names = ["get", "put", "delete"]


class NewsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    permission_classes = [NewsDetailsPermissions]
    http_method_names = ["get", "put", "delete"]

    def perform_update(self, serializer):
        location = validate_location(self.request.data.get('location'))
        if location:
            serializer.save(modified_by=self.request.user, location=location)
        else:
            serializer.save(modified_by=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NewsGetSerializer
        return NewsSerializer


class NewsStatus(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={
        status.HTTP_200_OK: NewsUpdateStatusSerializer,
        status.HTTP_400_BAD_REQUEST: NewsUpdateStatusSerializer
    })
    def put(self, request, pk, format=None):

        news = self.get_object(pk)
        group = self.user_group(request)

        serializer = NewsUpdateStatusSerializer(news, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        pub_status = serializer.validated_data["status"].id

        if not group or \
                group == "app-user" and (pub_status not in (1, 2) or news.created_by != self.request.user) or \
                group == "app-moderator" and pub_status not in (1, 2, 3, 4, 5, 6):
            raise PermissionDenied

        serializer.save()
        return Response(serializer.data)

    def get_object(self, pk):
        try:
            return News.objects.get(pk=pk)
        except News.DoesNotExist:
            raise Http404

    @staticmethod
    def user_group(request):
        if not request.user.is_authenticated:
            return None
        try:
            user_groups = [g.name for g in request.user.groups.all()]
        except AttributeError:
            user_groups = []

        if "app-admin" in user_groups:
            return "app-admin"
        if "app-moderator" in user_groups:
            return "app-moderator"
        return "app-user"


class ReviewListCreate(generics.ListCreateAPIView):
    queryset = PubReviews.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppModeratorOrAdmin]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PubReviewGetSerializer
        elif self.request.method == 'POST':
            return PubReviewCreateSerializer
        return PubReviewUpdateSerializer


class ReviewDetailsUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = PubReviews.objects.all()
    permission_classes = [IsOwnerAndReadOnly | IsAppModeratorOrAdmin]
    http_method_names = ["get", "put", "delete"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PubReviewGetSerializer
        elif self.request.method == 'POST':
            return PubReviewCreateSerializer
        return PubReviewUpdateSerializer


class ReviewCommentsView(APIView):
    permission_classes = [IsAppModeratorOrAdmin | IsOwnerAndReadOnly]

    @swagger_auto_schema(responses={
        status.HTTP_201_CREATED: PubReviewCommentsSerializer,
        status.HTTP_400_BAD_REQUEST: PubReviewCommentsSerializer,
    })
    def post(self, request, pk, format=None):
        serializer = PubReviewCommentsSerializer(data={**request.data, "review": pk})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={status.HTTP_200_OK: PubReviewCommentsSerializer})
    def get(self, request, pk, format=None):
        comments = ReviewComments.objects.filter(review__id=pk)
        serializer = PubReviewCommentsSerializer(comments, many=True)
        return Response(serializer.data)


class NewsReviewCommentsView(APIView):
    permission_classes = [IsAppModeratorOrAdmin | IsOwnerAndReadOnly]

    @swagger_auto_schema(responses={
        status.HTTP_201_CREATED: NewsReviewCommentsSerializer,
        status.HTTP_400_BAD_REQUEST: NewsReviewCommentsSerializer,
    })
    def post(self, request, pk, format=None):
        serializer = NewsReviewCommentsSerializer(data={**request.data, "news": pk})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={status.HTTP_200_OK: NewsReviewCommentsSerializer})
    def get(self, request, pk, format=None):
        comments = NewsReviewComments.objects.filter(news__id=pk)
        serializer = NewsReviewCommentsSerializer(comments, many=True)
        return Response(serializer.data)


class StatusTypesList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(responses={status.HTTP_200_OK: PubStatusSerializer})
    def get(self, request, format=None):
        status_types = StatusTypes.objects.all()
        serializer = PubStatusSerializer(status_types, many=True)
        return Response(serializer.data)

