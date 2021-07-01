from rest_framework import serializers

from feeds.models import FeedPoll, FeedPollQuestion, FeedPollChoice
from users.models import User


class FeedPollAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedPollChoice
        fields = ["user"]
        extra_kwargs = {"user": {"read_only": True}}


class FeedPollQuestionCreateSerializer(serializers.ModelSerializer):
    percent = serializers.SerializerMethodField(method_name="get_percent", read_only=True)

    class Meta:
        model = FeedPollQuestion
        fields = ["id", "name", "percent"]

    @classmethod
    def get_percent(cls, obj):
        if obj.poll.count_vote:
            return obj.answers.count() / obj.poll.count_vote * 100
        return 0


class FeedPollCreateSerializer(serializers.ModelSerializer):
    results = FeedPollQuestionCreateSerializer(many=True)
    is_vote_self = serializers.SerializerMethodField(method_name="get_is_vote_self", read_only=True)
    count_value = serializers.SerializerMethodField(method_name="get_count_value", read_only=True)

    class Meta:
        model = FeedPoll
        fields = ["id", "name", "stoped", "anonymous", "multi_results", "results", "is_vote_self", "count_value"]

    def get_is_vote_self(self, obj):
        if self.context.get("created_signal", None):
            return True
        return FeedPollChoice.objects.filter(user=self.context.get("request_user"), answer__poll=obj).exists()

    @classmethod
    def get_count_value(cls, obj):
        return FeedPollChoice.objects.filter(answer__poll=obj).values_list("user__email", flat=True).distinct().count()


class FeedPollUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedPoll
        fields = ["stoped", "anonymous", "multi_results"]


class FeedPollChoiceCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    answer = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=FeedPollQuestion.objects.all(), required=False)
    )

    class Meta:
        model = FeedPollChoice
        fields = ["id", "user", "answer"]

    @classmethod
    def validate_unique_user_answer(cls, answers, user):
        if FeedPollChoice.objects.filter(answer__in=answers, user=user).exists():
            raise serializers.ValidationError({"user": "you have already voted"})

    @classmethod
    def validate_stoped(cls, instance):
        if instance.stoped:
            raise serializers.ValidationError({"stoped": "poll is stoped"})

    @classmethod
    def validate_is_poll_point(cls, poll, answers):
        if not poll.results.filter(poll__results__in=answers).exists():
            raise serializers.ValidationError({"answer": "these answers do not belong to the current poll"})

    def validate(self, attrs):
        attrs["user"] = self.context.get("user")
        attrs["poll"] = self.context.get("poll")
        self.validate_stoped(instance=attrs["poll"])
        self.validate_is_poll_point(poll=attrs["poll"], answers=attrs["answer"])
        return attrs
