from rest_framework import serializers

from feeds.models import FeedView


class FeedViewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedView
        fields = ["user"]
