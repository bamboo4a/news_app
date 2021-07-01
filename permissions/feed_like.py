from rest_framework.permissions import IsAuthenticated

from feeds.models import FeedLike, Feed


class FeedLikeDeletePermission(IsAuthenticated):
    def has_permission(self, request, view):
        if getattr(view, "swagger_fake_view", False):
            return True
        return FeedLike.objects.filter(id=view.kwargs.get("like_id")).first().user == request.user


class FeedLikeCreatePermission(IsAuthenticated):
    """
    Проверка на возможность создать лайк
    """

    def has_permission(self, request, view):
        if getattr(view, "swagger_fake_view", False):
            return True
        return (
            Feed.objects.filter(id=view.kwargs.get("feed_id"))
            .first()
            .team.team_members.filter(user=request.user)
            .exists()
        )
