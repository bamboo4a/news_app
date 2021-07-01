from django.urls import path
from feeds.views.feed_file import FeedFileViewSet


feed_file_create = FeedFileViewSet.as_view({"post": "create"})
feed_file_delete = FeedFileViewSet.as_view({"delete": "destroy"})
feed_file_list = FeedFileViewSet.as_view({"get": "list"})

urlpatterns = [
    path("<int:team_id>/create/", feed_file_create),
    path("<int:feed_id>/delete/<uuid:file_id>/", feed_file_delete),
    path("<int:feed_id>/list/", feed_file_list),
]
