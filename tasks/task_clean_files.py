from celery import shared_task

from feeds.models import FeedFile
from django.utils import timezone


__all__ = ["run_clean_feed_files_workload"]


@shared_task
def run_clean_feed_files_workload() -> None:
    """
    Очистка файлов фида
    """
    last_day = timezone.now() - timezone.timedelta(minutes=1)
    FeedFile.objects.filter(created_at__lte=last_day, feed__isnull=True).delete()
