from __future__ import annotations

from django.utils import timezone

from api.models import TimetableEntry


def get_active_timetable_entry(class_name: str, at=None):
    if not class_name:
        return None

    local_dt = timezone.localtime(at or timezone.now())
    weekday_key = local_dt.strftime("%A").lower()
    current_time = local_dt.time()

    return (
        TimetableEntry.objects.select_related("school_class", "faculty")
        .filter(
            school_class__name=class_name,
            is_active=True,
            day_of_week=weekday_key,
            start_time__isnull=False,
            end_time__isnull=False,
            start_time__lte=current_time,
            end_time__gt=current_time,
        )
        .order_by("start_time")
        .first()
    )


def resolve_current_period_for_class(class_name: str, at=None):
    entry = get_active_timetable_entry(class_name=class_name, at=at)
    if not entry:
        return None, None
    return entry.period, entry
