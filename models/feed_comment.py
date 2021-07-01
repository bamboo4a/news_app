from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.db import models
from feeds.models.feed import Feed
from users.models.user import User


class FeedComment(MPTTModel):
    comment_text = models.TextField(verbose_name="текст комментария")
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="feed_comments", verbose_name="пост фида")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="пользователь")
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="родительский комментарий",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="время создания")

    class MPTTMeta:
        order_insertion_by = ["created_at"]
