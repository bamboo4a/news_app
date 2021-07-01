from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from feeds.models import Feed
from teams.choices.role import RoleChoices
from teams.models import TeamMember

__all__ = ("FeedFileCreatePermission", "FeedFileDeletePermission", "FeedFileListPermission")


class FeedFileCreatePermission(IsAuthenticated):
    """
    Проверка может ли пользователь создать файл к фиду
    """

    def has_permission(self, request, view):
        if getattr(view, "swagger_fake_view", False):
            return True
        return TeamMember.objects.filter(team__id=view.kwargs.get("team_id"), user=request.user).exists()


class FeedFileDeletePermission(IsAuthenticated):
    """
    Проверка может ли пользователь удалить файл к фиду
    """

    def has_permission(self, request, view):
        if getattr(view, "swagger_fake_view", False):
            return True
        is_team_member_admin = (
            TeamMember.objects.filter(
                team_id=Feed.objects.filter(id=view.kwargs.get("feed_id")).first().team.id,
                user=request.user,
                role__in=[RoleChoices.ADMIN, RoleChoices.OWNER, RoleChoices.SUPERADMIN],
            )
            .active()
            .exists()
        )
        return (
            is_team_member_admin or Feed.objects.filter(id=view.kwargs["feed_id"]).first().created_by == request.user
        )


class FeedFileListPermission(IsAuthenticated):
    """
    Проверка: является ли юзер участником команды
    """

    def has_permission(self, request, view):
        if getattr(view, "swagger_fake_view", False):
            return True
        instance_feed = get_object_or_404(Feed, id=view.kwargs.get("feed_id"))
        return TeamMember.objects.filter(team_id=instance_feed.team_id, user=request.user).active().exists()
