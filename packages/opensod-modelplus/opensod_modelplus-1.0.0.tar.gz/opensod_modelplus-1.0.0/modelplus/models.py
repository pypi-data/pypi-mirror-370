from collections.abc import Iterable
from typing import TypeVar, override

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models import Q
from django.db.models.base import ModelBase
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .middleware import CurrentUserMiddleware


class CurrentUserMixin(models.Model):
    """
    An abstract base class model which provides method to get current user.

    Defines method:

    - get_current_user() - Get current user from CurrentUserMiddleware.
    """

    class Meta:
        """Meta class."""

        abstract = True

    @staticmethod
    def get_current_user() -> AbstractBaseUser | int | None:
        """
        Get current user from CurrentUserMiddleware.

        Can be overwritten to use other middleware or additional
        functionality.

        :return: Instance of settings.AUTH_USER_MODEL
        """
        return CurrentUserMiddleware.get_current_user()


# ----------------------------------------------------------------------
class ActivatableQuerySet(models.QuerySet):
    """
    Queryset methods for filtering active/inactive instances.

    Should be used as a mixin for querysets that describe model which
    has ActivatableModel as parent.

    Defines filters:

    - active() - Returns active objects.
    - inactive() - Returns objects that are not active.

    E.g.:
      Define child queryset:
          class ChildQuerySet(ActivatableQuerySet):

      In child model class define:
          objects = ChildQuerySet.as_manager()
    """

    def active(self) -> models.QuerySet:
        """Filter active instances."""
        return self.filter(is_active=True)

    def inactive(self) -> models.QuerySet:
        """Filter inactive instances."""
        return self.filter(is_active=False)


# ----------------------------------------------------------------------
class ActivatableModel(models.Model):
    """
    An abstract base class model which provides activating instances.

    Defines fields:

    - is_active - Active flag. By default instance is active.
    """

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
    )

    class Meta:
        """Meta class."""

        abstract = True


# ----------------------------------------------------------------------
class CancellableQuerySet(models.QuerySet):
    """
    Queryset methods for filtering cancelled/not cancelled instances.

    Should be used as a mixin for querysets that describe model which
    has CancellableModel as parent.

    Defines filters:

    - cancelled() - Returns cancelled objects.
    - not_cancelled() - Returns objects that are not cancelled.

    E.g.:
      Define child queryset:
          class ChildQuerySet(CancellableQuerySet)

      In child model class define:
          objects = ChildQuerySet.as_manager()
    """

    def cancelled(self) -> models.QuerySet:
        """Filter cancelled instances."""
        return self.filter(is_cancelled=True)

    def not_cancelled(self) -> models.QuerySet:
        """Filter not cancelled instances."""
        return self.filter(is_cancelled=False)


# ----------------------------------------------------------------------
class CancellableModel(models.Model):
    """
    An abstract base class model which provides cancelling instances.

    Defines fields:

    - is_cancelled - Cancelled flag. By default instance is not cancelled.
    """

    is_cancelled = models.BooleanField(
        default=False,
        verbose_name=_("is cancelled"),
    )

    class Meta:
        """Meta class."""

        abstract = True


# ----------------------------------------------------------------------
class CancellationQuerySet(models.QuerySet):
    """
    Queryset methods for filtering instances cancelled by a user.

    Should be used as a mixin for querysets that describe model which
    has CancellationModel as parent.

    Object is considered cancelled if any of the fields
    cancelled_at or cancelled_by has been set to not null value.
    Contents of field cancellation_reason does not count in determining
    that the object has been cancelled.

    Defines filters:

    - cancelled() - Returns cancelled objects.
    - not_cancelled() - Returns objects that are not cancelled.
    - cancelled_by(user) - Returns objects cancelled by user.

    E.g.:
      Define child queryset:
          class ChildQuerySet(CancelledQuerySet)

      In child model class define:
          objects = ChildQuerySet.as_manager()
    """

    def cancelled(self) -> models.QuerySet:
        """
        Filter cancelled instances.

        Object is considered cancelled if any of the fields
        cancelled_at or cancelled_by has been set to not null value.
        """
        return self.filter(
            Q(cancelled_at__isnull=False) | Q(cancelled_by__isnull=False),
        )

    def not_cancelled(self) -> models.QuerySet:
        """
        Filter not cancelled instances.

        Object is considered not cancelled if both fields
        cancelled_at and cancelled_by are null.
        """
        return self.filter(
            cancelled_at__isnull=True,
            cancelled_by__isnull=True,
        )

    def cancelled_by(self, user: AbstractBaseUser | int) -> models.QuerySet:
        """
        Filter instances cancelled by user.

        :user: Instance of settings.AUTH_USER_MODEL or user id
        """
        return self.filter(cancelled_by=user)


# ----------------------------------------------------------------------
class CancellationModel(models.Model):
    """
    An abstract base class model which provides attributes for cancellation.

    Model instance is considered cancelled if any of the fields
    cancelled_at or cancelled_by has been set to not null value.
    Contents of field cancellation_reason does not count in determining
    that the instance has been cancelled.

    Defines fields:

    - cancelled_at - Date and time of cancellation. By default set to timezone.now.
    - cancelled_by - User that cancelled instance.
    - cancellation_reason - Description of reason for cancellation.
    """

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        default=now(),
        verbose_name=_("cancelled at"),
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_cancelled_by",
        verbose_name=_("cancelled by"),
    )
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name=_("cancellation reason"),
    )

    class Meta:
        """Meta class."""

        abstract = True


# ----------------------------------------------------------------------
class LockableQuerySet(models.QuerySet):
    """
    Queryset methods for filtering locked/unlocked instances.

    Should be used as a mixin for querysets that describe model which
    has LockableModel as parent.

    Defines filters:

    - locked() - Returns locked objects.
    - unlocked() - Returns objects that are not locked.

    E.g.:
      Define child queryset:
          class ChildQuerySet(LockableQuerySet)

      In child model class define:
          objects = ChildQuerySet.as_manager()
    """

    def locked(self) -> models.QuerySet:
        """Filter locked instances."""
        return self.filter(is_locked=True)

    def unlocked(self) -> models.QuerySet:
        """Filter unlocked instances."""
        return self.filter(is_locked=False)


# ----------------------------------------------------------------------
class LockableModel(models.Model):
    """
    An abstract base class model which provides locking instances.

    Defines fields:

    - is_locked - Locked flag. By default instance is unlocked.
    """

    is_locked = models.BooleanField(
        default=False,
        verbose_name=_("is locked"),
    )

    class Meta:
        """Meta class."""

        abstract = True


# ----------------------------------------------------------------------
class TimestampableModel(models.Model):
    """
    An abstract base class model which provides timestamps fields.

    Defines fields:

    - created_at - Date and time of instance creation, set automatically
                   on creation.
    - updated_at - Date and time of instance update, set automatically
                   on update.

    Time-stamps are populated using pre_save signal timestampable.
    Unfortunately, creating and updating objects in bulk doesn't
    update created_by and modified_by fields, since pre_save is not
    called.
    """

    created_at = models.DateTimeField(
        blank=True,
        editable=False,
        auto_now_add=True,
        verbose_name=_("created at"),
    )
    updated_at = models.DateTimeField(
        blank=True,
        editable=False,
        auto_now=True,
        verbose_name=_("updated at"),
    )

    class Meta:
        """Meta class."""

        abstract = True
        get_latest_by = "updated_at"


# ----------------------------------------------------------------------
class UserstampableQuerySet(models.QuerySet):
    """
    Queryset methods for filtering instances created by a user.

    Should be used as a mixin for querysets that describe model which
    has UserstampableModel as parent.

    Defines filters:

    - created_by(user) - Returns objects created by user.
    - updated_by(user) - Returns objects updated by user.

    E.g.:
      Define child queryset:
          class ChildQuerySet(UserstampableQuerySet)

      In child model class define:
          objects = ChildQuerySet.as_manager()
    """

    def created_by(self, user: AbstractBaseUser | int) -> models.QuerySet:
        """
        Filter instances created by user.

        :user: Instance of settings.AUTH_USER_MODEL or user id.
        """
        return self.filter(created_by=user)

    def updated_by(self, user: AbstractBaseUser | int) -> models.QuerySet:
        """
        Filter instances updated by user.

        :user: Instance of settings.AUTH_USER_MODEL or user id.
        """
        return self.filter(updated_by=user)


# ----------------------------------------------------------------------
class UserstampableModel(CurrentUserMixin):
    """
    An abstract base class model which provides userstamp fields.

    Defines fields:

    - created_by - User that created instance. Automatically set to
                   current user on creation.
    - updated_by - User that updated instance. Automatically set to
                   current user on update.

    Deletion of the referenced created_by and modified_by objects is
    protected.

    `modelplus.middleware.CurrentUserMiddleware` must be added to
    settings.MIDDLEWARE after
    `django.contrib.auth.middleware.AuthenticationMiddleware`.

    Inherites methods:

    - get_current_user() [CurrentUserMixin]
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_updated_by",
        verbose_name=_("updated by"),
    )

    class Meta:
        """Meta class."""

        abstract = True

    @override
    def save(
        self,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        """Override save method to update created_by and updated_by fields."""
        current_user = self.get_current_user()
        if self._state.adding is True:
            self.created_by = current_user
        self.updated_by = current_user

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
