from django.db import transaction
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from feeds.models import FeedPollChoice, FeedPollQuestion, FeedPoll, Feed
from feeds.serializers.feed import FeedCreateSerializer
from feeds.serializers.feed_poll import (
    FeedPollChoiceCreateSerializer,
    FeedPollUpdateSerializer,
)
from rest_framework import generics

from users.models import User
from rest_framework.response import Response


class FeedPollChoiceCreateView(generics.CreateAPIView):
    queryset = FeedPollChoice.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FeedPollChoiceCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                "user": get_object_or_404(User, id=self.request.user.id),
                "poll": get_object_or_404(FeedPoll, id=self.kwargs.get("poll_id")),
            }
        )
        return context

    @classmethod
    @transaction.atomic()
    def remove_old_votes(cls, poll, user):
        old_votes = FeedPollChoice.objects.filter(answer__poll=poll, user=user)
        count = len(old_votes)
        if poll.count_vote >= count:
            poll.update_count_vote(count=count, arithmetic_sign="-")
        else:
            poll.count_vote = count
        old_votes.delete()

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(id=serializer.data.get("user"))
        poll = FeedPoll.objects.get(id=self.kwargs.get("poll_id"))
        answers = FeedPollQuestion.objects.filter(id__in=serializer.data.get("answer"))
        self.remove_old_votes(poll=poll, user=user)
        for answer in answers:
            FeedPollChoice.objects.create(answer=answer, user=user)
        poll.update_count_vote(count=len(answers), arithmetic_sign="+")
        poll.save()
        feed = Feed.objects.filter(poll=poll).first()
        # передача сериализатора сигнала о том, что нужно принудительно выставить флаг is_vote_self = True
        return Response(FeedCreateSerializer(instance=feed, context={"created_signal": "created"}).data)


class FeedPollChoiceUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedPollUpdateSerializer
    lookup_url_kwarg = "poll_id"

    def get_object(self):
        return get_object_or_404(FeedPoll, id=self.kwargs.get("poll_id"))
