from rest_framework import serializers
from feeds.models.feed_comment import FeedComment


__all__ = (
    "FeedCommentCreateSerializer",
    "FeedCommentUpdateSerializer",
    "FeedCommentListParentSerializer",
    "FeedCommentListChildrenSerializer",
)

from feeds.serializers.feed_recipients import FeedUserDetailSerializer

from users.models import User


class FeedCommentCreateSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=FeedComment.objects.all(), required=True, allow_null=True)
    feed = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = FeedComment
        fields = ["comment_text", "feed", "created_by", "parent", "created_at", "tree_id", "id"]

    def validate(self, attrs):
        attrs["feed"] = self.context["feed"]
        attrs["created_by"] = self.context["created_by"]
        super().validate(attrs)
        # check for max nested comments
        if attrs["parent"]:
            parent = attrs["parent"]
            if parent.get_level() >= 9:
                raise serializers.ValidationError(
                    {"error": "Допущена максимально допустимая вложенность комментария", "const": ""}
                )
        return attrs

    def create(self, validated_data):
        new_instance = FeedComment.objects.create(
            comment_text=validated_data["comment_text"],
            created_by=validated_data["created_by"],
            parent=validated_data["parent"],
            feed=validated_data["feed"],
        )
        return new_instance

    @property
    def data(self):
        return FeedCommentSerializer(instance=self.instance, context=self.context).data


class FeedCommentSerializer(serializers.ModelSerializer):
    created_by = FeedUserDetailSerializer()

    class Meta:
        model = FeedComment
        fields = ["created_by", "comment_text", "feed", "parent", "created_at", "tree_id", "id"]
        read_only_fields = fields


class FeedCommentUpdateSerializer(serializers.ModelSerializer):
    comment_text = serializers.CharField(required=True)
    feed = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = FeedComment
        fields = ["comment_text", "feed", "created_by", "parent", "created_at", "tree_id", "id"]

    def get_created_by(self, instance):
        return FeedUserDetailSerializer(instance.created_by, context=self.context, read_only=True).data


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class FeedCommentListParentSerializer(serializers.ModelSerializer):
    is_have_childrens = serializers.SerializerMethodField(read_only=True)
    created_by = FeedUserDetailSerializer()

    class Meta:
        model = FeedComment
        fields = [
            "comment_text",
            "feed",
            "created_by",
            "parent",
            "created_at",
            "tree_id",
            "id",
            "level",
            "is_have_childrens",
        ]

    @classmethod
    def get_is_have_childrens(cls, obj):
        return not obj.is_leaf_node()


class FeedCommentListChildrenSerializer(serializers.ModelSerializer):
    is_have_childrens = serializers.SerializerMethodField(read_only=True)
    children = RecursiveField(many=True, read_only=True)
    created_by = FeedUserDetailSerializer()

    class Meta:
        model = FeedComment
        fields = [
            "comment_text",
            "feed",
            "created_by",
            "parent",
            "created_at",
            "tree_id",
            "id",
            "level",
            "is_have_childrens",
            "children",
        ]

    @classmethod
    def get_is_have_childrens(cls, obj):
        return not obj.is_leaf_node()
