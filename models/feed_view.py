from django.db import models

from feeds.models import Feed
from users.models import User


class FeedView(models.Model):
    feed = models.ForeignKey(Feed, verbose_name="фид", related_name="feed_views", on_delete=models.CASCADE)

    user = models.ForeignKey(
        User, verbose_name="пользователь", related_name="user_feed_views", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ["feed", "user"]

    def __str__(self):
        return f"feed: {self.feed}, user: {self.user}"
