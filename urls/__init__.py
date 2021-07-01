from django.urls import include, path

app_name = "feeds"

urlpatterns = [
    path("feed/", include("feeds.urls.feed")),
    path("files/", include("feeds.urls.feed_file")),
    path("comment/", include("feeds.urls.feed_comment")),
    path("like/", include("feeds.urls.feed_like")),
    path("poll/", include("feeds.urls.feed_poll")),
]
