from django.urls import path

from feeds.views.feed_like import FeedLikeCreateDeleteListView

like_create = FeedLikeCreateDeleteListView.as_view({"post": "create"})
like_delete = FeedLikeCreateDeleteListView.as_view({"delete": "destroy"})

urlpatterns = [
    path("<int:feed_id>/create/", like_create),
    path("<int:like_id>/delete/", like_delete),
]
