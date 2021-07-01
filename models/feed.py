from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from feeds.models import FeedPoll
from teams.models.team import Team
from projects.models.project import Project
from users.models.user import User

class Feed(models.Model):

    team = models.ForeignKey(Team, related_name="team_feeds", on_delete=models.CASCADE, verbose_name="Команда")
    project = models.ForeignKey(
        Project,
        related_name="project_feeds",
        on_delete=models.CASCADE,
        verbose_name="Проект",
        null=True,
        default=None,
    )
    description = models.JSONField(encoder=DjangoJSONEncoder, default=dict, verbose_name="Описание")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="feed_created",
        verbose_name="Создатель",
        null=True,
        blank=True,
    )
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_have_comments = models.BooleanField(verbose_name="Есть ли комментарии", default=False)
    poll = models.OneToOneField(
        FeedPoll,
        on_delete=models.SET_NULL,
        verbose_name="Опрос",
        null=True,
        default=None
    )

    def __str__(self):
        return f"Feed id:{self.id}, team:{self.team}, project:{self.project}"
