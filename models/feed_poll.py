from django.db import models

from users.models import User


__all__ = ["FeedPoll", "FeedPollQuestion", "FeedPollChoice"]


class FeedPoll(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название опроса")
    stoped = models.BooleanField(default=False, verbose_name="Оставлено ли голосование")
    anonymous = models.BooleanField(verbose_name="Является ли опрос анонимным")
    multi_results = models.BooleanField(verbose_name="Допускается ли голосовать за несколько вариантов")
    count_vote = models.PositiveBigIntegerField(verbose_name="Общее количество голосов", default=0)

    def __str__(self):
        return f"Feed-poll: {self.name}"

    def update_count_vote(self, count: int, arithmetic_sign: str):
        if arithmetic_sign == "+":
            self.count_vote += count
        elif arithmetic_sign == "-":
            self.count_vote -= count


class FeedPollQuestion(models.Model):
    name = models.CharField(max_length=255, verbose_name="Вопрос")
    poll = models.ForeignKey(
        FeedPoll,
        on_delete=models.CASCADE,
        verbose_name="Опрос",
        related_name="results",
        null=True,
        default=None,
    )

    def __str__(self):
        return f"Feed-poll: {self.poll}, question: {self.name}"


class FeedPollChoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    answer = models.ForeignKey(
        FeedPollQuestion, verbose_name="Вопрос", related_name="answers", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Feed-poll question: {self.answer}; User: {self.user}"
