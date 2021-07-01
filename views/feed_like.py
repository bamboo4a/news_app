from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from feeds.models import FeedLike, Feed
from feeds.permissions.feed_like import FeedLikeCreatePermission, FeedLikeDeletePermission
from feeds.serializers.feed_like import FeedLikeCreateSerializer

__all__ = ["FeedLikeCreateDeleteListView"]


class FeedLikeCreateDeleteListView(ModelViewSet):
    queryset = FeedLike.objects.all()

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, FeedLikeCreatePermission]
        if self.action == "destroy":
            self.permission_classes = [IsAuthenticated, FeedLikeDeletePermission]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return FeedLikeCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(FeedLike, id=self.kwargs.get("like_id"))
        instance.delete()
        return Response({"delete": "success"})

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.action == "create":
            ctx.update({"feed": get_object_or_404(Feed, id=self.kwargs.get("feed_id"))})
        return ctx
