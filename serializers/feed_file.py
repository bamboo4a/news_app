from rest_framework import serializers
from feeds.models.feed_file import FeedFile


class FeedFileListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="filename", read_only=True)
    size = serializers.CharField(read_only=True)
    size_kb = serializers.CharField(read_only=True)
    extension = serializers.CharField(source="file_extension", read_only=True)

    class Meta:
        model = FeedFile
        fields = [
            "id",
            "name",
            "file",
            "created_at",
            "size",
            "size_kb",
            "extension",
        ]


class FeedFileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedFile
        fields = ["file"]

    def create(self, validated_data):
        validated_data["team"] = self.context.get("team")
        instance = super().create(validated_data)
        return instance

    @property
    def data(self):
        return FeedFileListSerializer(instance=self.instance, context=self.context).data
