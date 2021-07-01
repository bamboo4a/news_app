from django.db import models

from feeds.models import Feed
from users.models import User


class FeedLike(models.Model):
    feed = models.ForeignKey(Feed, related_name="feed_likes", verbose_name="лайки", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="user_feed_likes", verbose_name="пользователь", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ["feed", "user"]

    def __str__(self):
        return f"feed: {self.feed_id} - user: {self.user_id}"
