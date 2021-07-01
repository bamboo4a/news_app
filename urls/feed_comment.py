from django.urls import path
from feeds.views.feed_comment import FeedCommentViewSet, FeedCommentFirstStepListView, FeedCommentChildListView


comment_create = FeedCommentViewSet.as_view({"post": "create"})
comment_update = FeedCommentViewSet.as_view({"patch": "partial_update"})
comment_delete = FeedCommentViewSet.as_view({"delete": "destroy"})
comment_parent_list = FeedCommentFirstStepListView.as_view()
comment_child_list = FeedCommentChildListView.as_view()

urlpatterns = [
    path("<int:feed_id>/create/", comment_create),
    path("<int:feed_id>/update/<int:feed_comment_id>/", comment_update),
    path("<int:feed_id>/delete/<int:feed_comment_id>/", comment_delete),
    path("<int:feed_id>/list-first/", comment_parent_list),
    path("<int:feed_id>/get-childrens/<int:parent_id>/", comment_child_list),
]
