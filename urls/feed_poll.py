from django.urls import path

from feeds.views.feed_poll import FeedPollChoiceCreateView, FeedPollChoiceUpdateView

urlpatterns = [
    path("<int:poll_id>/vote/", FeedPollChoiceCreateView.as_view()),
    path("<int:poll_id>/update/", FeedPollChoiceUpdateView.as_view()),
]
