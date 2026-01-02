from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import WorkSession
from . import services


@receiver(post_save, sender=WorkSession)
def recompute_summary_on_session_save(sender, instance, **kwargs):
    if instance.clock_out_at and instance.total_work_duration:
        # Reuse the tested logic in services
        services._update_daily_summary_for_session(instance)
