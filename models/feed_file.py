from django.db import models
from feeds.models.feed import Feed
from teams.models import Team
from utils.models import FileAbstractModel
from pathlib import Path
from django.utils import timezone


def get_upload_path(instance, filename):
    now = timezone.now()
    today_path = now.strftime("%Y/%m/%d")
    team_id = instance.team.id
    return Path(f"teams/{team_id}/files/feeds/{today_path}/{filename}")


class FeedFile(FileAbstractModel):
    feed = models.ForeignKey(
        Feed, related_name="feed_files", on_delete=models.CASCADE, verbose_name="Файлы фида", default=None, null=True
    )
    team = models.ForeignKey(
        Team, verbose_name="Команда", on_delete=models.CASCADE, related_name="team_feed_files", default=None
    )
    file = models.FileField("Файл", upload_to=get_upload_path)

    class Meta:
        verbose_name = "Файл фида"
        verbose_name_plural = "Файлы фидов"
