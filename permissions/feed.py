from rest_framework.permissions import IsAuthenticated


from feeds.models import Feed
from teams.choices.role import RoleChoices
from teams.models import TeamMember

__all__ = ("FeedDeletePermission", "FeedCreatePermission")


class FeedDeletePermission(IsAuthenticated):
    """
    Проверка может ли пользователь удалить пост Feed
    """

    def has_permission(self, request, view):
        if getattr(view, "swagger_fake_view", False):
            return True
        is_team_member_admin = (
            TeamMember.objects.filter(
                team_id=view.kwargs.get("team_id"),
                user=request.user,
                role__in=[RoleChoices.ADMIN, RoleChoices.OWNER, RoleChoices.SUPERADMIN],
            )
            .active()
            .exists()
        )
        return (
            is_team_member_admin or Feed.objects.filter(id=view.kwargs["feed_id"]).first().created_by == request.user
        )


class FeedCreatePermission(IsAuthenticated):
    """
    Проверка: является ли юзер участником команды
    """

    def has_permission(self, request, view):
        if getattr(view, "swagger_fake_view", False):
            return True
        return TeamMember.objects.filter(team_id=view.kwargs.get("team_id"), user=request.user).active().exists()
