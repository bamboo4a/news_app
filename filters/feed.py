from django_filters.rest_framework import FilterSet, NumberFilter, BooleanFilter

from feeds.models import Feed

__all__ = ("FeedFilter",)


class FeedFilter(FilterSet):
    project = NumberFilter(field_name="project")
    team = NumberFilter(field_name="team")
    recipient = NumberFilter(method="filter_recipient")
    without_recipient = BooleanFilter(method="filter_without_recipient")
    created_by = NumberFilter(field_name="created_by")
    without_project = BooleanFilter(method="filter_without_project")

    class Meta:
        model = Feed
        fields = ["project", "team", "recipient", "created_by"]

    def filter_recipient(self, queryset, name, value):
        if value:
            return queryset.filter(feed_recipients__user_id=value)
        return queryset

    def filter_without_recipient(self, queryset, name, value):
        if value:
            return queryset.filter(feed_recipients__isnull=True)
        return queryset

    def filter_without_project(self, queryset, name, value):
        if value:
            return queryset.filter(project=None)
        return queryset
