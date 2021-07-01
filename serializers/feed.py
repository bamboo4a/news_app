from django.db import transaction
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from feeds.models import FeedRecipient, FeedFile, FeedPoll

from feeds.models.feed import Feed
from feeds.serializers.feed_file import FeedFileListSerializer
from feeds.serializers.feed_like import FeedLikeSerializer
from feeds.serializers.feed_poll import FeedPollCreateSerializer

from feeds.serializers.feed_recipients import FeedRecipientSerializer, FeedUserDetailSerializer
from feeds.serializers.feed_view import FeedViewListSerializer
from utils.models import User

__all__ = ("FeedListSerializer", "FeedUpdateSerializer", "FeedCreateSerializer")


class CreatedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [""]


class FeedListSerializer(serializers.ModelSerializer):
    description = serializers.JSONField()
    feed_recipients = FeedRecipientSerializer(many=True)
    feed_views = FeedViewListSerializer(many=True)
    feed_likes = FeedLikeSerializer(many=True)
    created_by = FeedUserDetailSerializer()
    feed_files = FeedFileListSerializer(many=True)
    poll = FeedPollCreateSerializer()
    is_have_comments = serializers.SerializerMethodField(method_name="get_is_have_comments")

    class Meta:
        model = Feed
        fields = [
            "id",
            "team",
            "project",
            "description",
            "created_date",
            "modified_date",
            "created_by",
            "feed_recipients",
            "feed_views",
            "feed_likes",
            "feed_files",
            "poll",
            "is_have_comments"
        ]

    @classmethod
    def get_is_have_comments(cls, obj):
        return obj.feed_comments.exists()


class FeedUpdateSerializer(serializers.ModelSerializer):

    description = serializers.JSONField(required=True)
    feed_files = serializers.ListField(child=serializers.UUIDField(), required=True)

    class Meta:
        model = Feed
        fields = ["description", "feed_files"]


class FeedUpdateResponseSerializer(serializers.ModelSerializer):

    description = serializers.JSONField(read_only=True)
    feed_files = FeedFileListSerializer(many=True)

    class Meta:
        model = Feed
        fields = ["description", "feed_files"]


class FeedCreateSerializer(serializers.Serializer):
    description = serializers.JSONField(required=True)
    feed_recipients = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()))
    feed_files = serializers.ListField(child=serializers.UUIDField(), required=True)
    poll = FeedPollCreateSerializer(required=True, allow_null=True)

    class Meta:
        model = Feed
        fields = ["team", "description", "project", "feed_recipients", "feed_files", "poll"]

    def validate(self, attrs):
        # проверка на существование файла
        for file_id in attrs.get("feed_files"):
            get_object_or_404(FeedFile, id=file_id)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data["team"] = self.context["team"]
        if self.context.get("project") is not None:
            validated_data["project"] = self.context["project"]
        validated_data["created_by"] = self.context["created_by"]
        feed_recipients = validated_data.pop("feed_recipients")
        feed_files = validated_data.pop("feed_files")
        feed_poll = validated_data.pop("poll")
        # create Feed:
        instance_feed = Feed.objects.create(**validated_data)
        if feed_poll:
            poll_questions = feed_poll.pop("results", None)
            # create FeedPoll
            new_poll = FeedPoll.objects.create(**feed_poll)
            instance_feed.poll = new_poll
            for poll in poll_questions:
                new_poll.results.create(**poll)
        # update FeedFile:
        FeedFile.objects.filter(id__in=feed_files).update(feed=instance_feed)
        # create feed_recipients
        for user in feed_recipients:
            FeedRecipient.objects.create(feed=instance_feed, user=user)
        instance_feed.save()
        return instance_feed

    @property
    def data(self):
        return FeedListSerializer(instance=self.instance, context=self.context).data
