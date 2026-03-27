from __future__ import annotations

from typing import Optional

from django.db.models import QuerySet

from api.models import CustomUser, SchoolClass, TimetableEntry


def is_principal(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    return bool(
        user.is_superuser
        or user.role in {CustomUser.ROLE_ADMIN, CustomUser.ROLE_PRINCIPAL}
    )


def get_managed_class_names(user) -> Optional[list[str]]:
    if not user or not getattr(user, "is_authenticated", False):
        return []
    if is_principal(user):
        return None

    incharge_classes = list(
        SchoolClass.objects.filter(incharge=user, is_active=True)
        .values_list("name", flat=True)
        .order_by("name")
    )

    taught_classes = list(
        TimetableEntry.objects.filter(
            faculty=user,
            is_active=True,
            school_class__is_active=True,
        )
        .values_list("school_class__name", flat=True)
        .order_by("school_class__name")
    )

    return sorted(set(incharge_classes).union(taught_classes))


def user_can_access_class(user, class_name: str) -> bool:
    managed_class_names = get_managed_class_names(user)
    if managed_class_names is None:
        return True
    return class_name in managed_class_names


def scope_queryset_to_user_classes(queryset: QuerySet, user, class_lookup: str) -> QuerySet:
    managed_class_names = get_managed_class_names(user)
    if managed_class_names is None:
        return queryset
    if not managed_class_names:
        return queryset.none()
    return queryset.filter(**{f"{class_lookup}__in": managed_class_names})
