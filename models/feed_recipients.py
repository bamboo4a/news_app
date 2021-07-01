from django.db import models

from butler_bot.models import User
from feeds.models import Feed


class FeedRecipient(models.Model):
    feed = models.ForeignKey(
        Feed, verbose_name="команда", related_name="feed_recipients", on_delete=models.CASCADE, default=None
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_recipients",
        verbose_name="пользователь",
    )

    class Meta:
        unique_together = ["feed", "user"]

    def __str__(self):
        return f"{self.feed} - {self.user}"
