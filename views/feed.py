from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from feeds.filters.feed import FeedFilter
from feeds.models import FeedView, FeedFile
from feeds.models.feed import Feed
from feeds.permissions.feed import FeedDeletePermission
from feeds.serializers.feed import (
    FeedCreateSerializer,
    FeedListSerializer,
    FeedUpdateSerializer,
    FeedUpdateResponseSerializer,
)
from projects.models import Project
from teams.models import Team
from rest_framework.response import Response
from feeds.pagination.feed import FeedPagination
from users.models import User

__all__ = ["FeedViewSet"]


class FeedViewSet(ModelViewSet):
    serializer_class = FeedCreateSerializer
    queryset = Feed.objects.all()
    pagination_class = FeedPagination
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["description"]

    filterset_class = FeedFilter
    ordering_fields = ["created_date"]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        project_id = self.request.data.get("project")
        team_id = self.kwargs.get("team_id")
        if project_id is not None:
            ctx.update({"project": get_object_or_404(Project, id=project_id)})
        if self.action == "create":
            ctx.update({"created_by": get_object_or_404(User, id=self.request.user.id)})
        if self.action == "list":
            ctx.update({"request_user": User.objects.filter(id=self.request.user.id).first()})
        ctx.update({"team": get_object_or_404(Team, id=team_id)})
        return ctx

    def get_permissions(self):
        if self.action == "destroy":
            self.permission_classes = [IsAuthenticated, FeedDeletePermission]
        elif self.action in ["create", "list"]:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return FeedCreateSerializer
        if self.action == "list":
            return FeedListSerializer
        if self.action == "partial_update":
            return FeedUpdateSerializer

    def get_queryset(self):
        if self.action == "list":
            team_id = self.kwargs.get("team_id")
            queryset = Feed.objects.filter(
                Q(team=team_id)
                & (
                    (Q(project__members__user_id=self.request.user.id) | Q(project=None))
                    & (
                        Q(feed_recipients__isnull=True)
                        | Q(
                            Q(feed_recipients__user_id=self.request.user.id)
                            & Q(
                                Q(feed_recipients__user__team_members__is_blocked=False)
                                | Q(feed_recipients__user__is_deleted=False)
                            )
                        )
                        | Q(created_by_id=self.request.user.id)
                    )
                )
            ).distinct()
            #  создание и обновление списка просмотревших данную запись
            for instance in queryset:
                if not FeedView.objects.filter(feed=instance, user=self.request.user).exists():
                    FeedView.objects.create(feed=instance, user=self.request.user)
            return queryset
        else:
            return self.queryset

    def destroy(self, request, *args, **kwargs):
        get_object_or_404(Feed, id=self.kwargs.get("feed_id")).delete()
        return Response({"delete": "success"}, status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = get_object_or_404(Feed, id=kwargs.get("feed_id"))
        # update field files
        new_feed_files = request.data["feed_files"]
        if new_feed_files:
            instance.feed_files.all().update(feed=None)
            FeedFile.objects.filter(id__in=new_feed_files).update(feed=instance)
        # update field description
        new_content = request.data["description"]
        instance.description = new_content
        FeedFile.objects.filter(id__in=new_feed_files).update(feed=instance)
        instance.save()
        response = FeedUpdateResponseSerializer(instance=instance).data

        return Response(response)
