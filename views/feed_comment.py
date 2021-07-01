from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from feeds.models import Feed
from feeds.models.feed_comment import FeedComment
from feeds.pagination.feed_comment import FeedCommentPagination
from feeds.permissions.feed_comment import FeedCommentListPermission, FeedCommentUpdatePermission
from feeds.serializers.feed_comment import (
    FeedCommentCreateSerializer,
    FeedCommentUpdateSerializer,
    FeedCommentListParentSerializer,
    FeedCommentListChildrenSerializer,
)
from users.models import User

__all__ = ("FeedCommentViewSet", "FeedCommentFirstStepListView", "FeedCommentChildListView")


class FeedCommentViewSet(ModelViewSet):
    """
    ViewSet for managing feed's comments
    """

    queryset = FeedComment.objects.all()
    # serializer_class = FeedCommentCreateSerializer
    lookup_url_kwarg = "feed_comment_id"

    def get_serializer_class(self):
        if self.action == "create":
            return FeedCommentCreateSerializer
        elif self.action == "partial_update":
            return FeedCommentUpdateSerializer
        elif self.action == "list":
            return FeedCommentListParentSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.action == "create":
            ctx.update(
                {
                    "feed": get_object_or_404(Feed, id=self.kwargs.get("feed_id")),
                    "created_by": get_object_or_404(User, id=self.request.user.id),
                }
            )
        return ctx

    def get_permissions(self):
        if self.action in ["create", "list"]:
            self.permission_classes = [IsAuthenticated, FeedCommentListPermission]
        elif self.action == "partial_update":
            self.permission_classes = [IsAuthenticated, FeedCommentUpdatePermission]
        return [permission() for permission in self.permission_classes]

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        instance.comment_text = request.data.get("comment_text")
        instance.save()
        response = self.get_serializer_class()(instance=instance, context=self.get_serializer_context()).data
        return Response(response)

    def destroy(self, request, *args, **kwargs):
        super(FeedCommentViewSet, self).destroy(request, *args, **kwargs)
        return Response({"deleted": "success"})


class FeedCommentFirstStepListView(generics.ListAPIView):
    """
    View for get first path comments
    """

    permission_classes = [IsAuthenticated, FeedCommentListPermission]
    serializer_class = FeedCommentListParentSerializer
    pagination_class = FeedCommentPagination

    def get_queryset(self):
        queryset = FeedComment.objects.filter(feed__id=self.kwargs.get("feed_id"), level=0).order_by("-created_at")
        return queryset


class FeedCommentChildListView(generics.ListAPIView):
    """
    View to show the children of the parent
    """

    permission_classes = [IsAuthenticated, FeedCommentListPermission]
    serializer_class = FeedCommentListChildrenSerializer
    pagination_class = FeedCommentPagination

    def get_queryset(self):
        return (
            FeedComment.objects.filter(feed__id=self.kwargs.get("feed_id"), id=self.kwargs.get("parent_id"))
            .first()
            .get_children()
        ).order_by("-created_at")
