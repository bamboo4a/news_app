from django.urls import path
from feeds.views.feed import FeedViewSet

feed_create = FeedViewSet.as_view({"post": "create"})
feed_list = FeedViewSet.as_view({"get": "list"})
feed_delete = FeedViewSet.as_view({"delete": "destroy"})
feed_update = FeedViewSet.as_view({"patch": "partial_update"})

urlpatterns = [
    path("<int:team_id>/create/", feed_create),
    path("<int:team_id>/list/", feed_list),
    path("<int:team_id>/delete/<int:feed_id>/", feed_delete),
    path("<int:team_id>/update/<int:feed_id>/", feed_update),
]
