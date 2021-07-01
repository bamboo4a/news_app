from rest_framework import serializers
from feeds.models import FeedLike
from django.utils.translation import gettext_lazy as _

class FeedLikeCreateSerializer(serializers.ModelSerializer):
    feed_id = serializers.IntegerField(required=False)

    class Meta:
        model = FeedLike
        fields = ["feed_id", "user", "id"]

    def validate(self, attrs):
        attrs["feed"] = self.context["feed"]
        if FeedLike.objects.filter(feed=attrs["feed"], user=attrs["user"]).exists():
            raise serializers.ValidationError({"error_message": _("Вы уже оценили эту запись")})
        return super().validate(attrs)

    def create(self, validated_data):
        instance = FeedLike.objects.create(**validated_data)
        return instance


class FeedLikeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedLike
        fields = ["feed", "user", "id"]
        read_only_fields = fields


class FeedLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedLike
        fields = ["user", "id"]
        read_only_fields = fields
