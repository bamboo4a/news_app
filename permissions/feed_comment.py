from rest_framework.permissions import IsAuthenticated

from feeds.models import Feed
from teams.choices.role import RoleChoices
from teams.models import TeamMember

__all__ = ("FeedCommentListPermission", "FeedCommentUpdatePermission")


class FeedCommentListPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if getattr(view, "swagger_fake_view", False):
            return True
        return (
            Feed.objects.filter(id=view.kwargs.get("feed_id"))
            .first()
            .team.team_members.filter(user=request.user)
            .exists()
        )


class FeedCommentUpdatePermission(IsAuthenticated):
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
            is_team_member_admin
            or Feed.objects.filter(id=view.kwargs.get("feed_id")).first().created_by == request.user
        )
