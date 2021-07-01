from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import get_object_or_404

from feeds.permissions.feed_file import FeedFileDeletePermission, FeedFileCreatePermission, FeedFileListPermission
from feeds.serializers.feed_file import FeedFileCreateSerializer, FeedFileListSerializer
from feeds.models.feed_file import FeedFile
from feeds.models.feed import Feed
from teams.models import Team


__all__ = ["FeedFileViewSet"]


class FeedFileViewSet(ModelViewSet):
    def get_queryset(self):
        if self.action == "list":
            return self.queryset.filter(feed_id=self.kwargs.get("feed_id"))
        else:
            return self.queryset

    def get_permissions(self):
        if self.action == "destroy":
            self.permission_classes = [IsAuthenticated, FeedFileDeletePermission]
        elif self.action == "create":
            self.permission_classes = [IsAuthenticated, FeedFileCreatePermission]
        elif self.action == "list":
            self.permission_classes = [IsAuthenticated, FeedFileListPermission]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return FeedFileCreateSerializer
        if self.action == "list":
            return FeedFileListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.action == "create":
            ctx.update({"team": get_object_or_404(Team, id=self.kwargs.get("team_id"))})
        else:
            ctx.update({"feed": get_object_or_404(Feed, id=self.kwargs.get("feed_id"))})
        return ctx

    def destroy(self, request, *args, **kwargs):
        instance_file = get_object_or_404(FeedFile, id=self.kwargs.get("file_id"))
        instance_file.file.delete(False)
        instance_file.delete()
        return Response({"delete": "success"}, status=status.HTTP_204_NO_CONTENT)
