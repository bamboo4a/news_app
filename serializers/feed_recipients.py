from rest_framework import serializers
from feeds.models.feed_recipients import FeedRecipient
from users.models import User


class FeedUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "avatar", "color"]
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["full_name"] = f"{instance.first_name} {instance.last_name}"
        return representation


class FeedRecipientSerializer(serializers.ModelSerializer):
    user = FeedUserDetailSerializer()

    class Meta:
        model = FeedRecipient
        fields = ["user"]
