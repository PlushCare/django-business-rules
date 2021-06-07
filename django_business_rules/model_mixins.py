from __future__ import absolute_import, division, print_function
from django.db import models

from plushcareAPI.time_helper import TimeHelper


class TimeStampAbstractMixin(models.Model):
    """
        This abstract mixin is used to add creation_timestamp and updated_timestamp fields to the model this is added to
        also it overrides the save method to update the creation_timestamp and updated_timestamp as needed
    """

    TIMESTAMP_FIELDSETS = ('creation_timestamp', 'updated_timestamp',)
    # timestamps
    creation_timestamp = models.DateTimeField(null=True, blank=True)
    updated_timestamp = models.DateTimeField(
        null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def update_timestamps(self):
        # get now as UTC
        utc_now = TimeHelper.get_utc_now_datetime()

        # if we have never been saved, then set the creation_timestamp to now(UTC)
        if not self.creation_timestamp:
            self.creation_timestamp = utc_now

        # always overwrite updated_timestamp to now(UTC) with every save
        self.updated_timestamp = utc_now

    def save(self, update_fields=None, *args, **kwargs):
        self.update_timestamps()
        if update_fields and 'updated_timestamp' not in update_fields:
            update_fields.append('updated_timestamp')
        super(TimeStampAbstractMixin, self).save(
            update_fields=update_fields, *args, **kwargs)


class TimeQuerySetMixin(models.QuerySet):
    start_key = ''
    end_key = ''

    def _start_kwargs(self, datetime, include=True):
        action = '__lte' if include else '__gt'
        key = '{}{}'.format(self.start_key, action)

        kwargs = {
            key: datetime
        }

        return kwargs

    def _end_kwargs(self, datetime, include=True):
        action = '__gt' if include else '__lte'
        key = '{}{}'.format(self.end_key, action)

        kwargs = {
            key: datetime
        }

        return kwargs

    def _full_kwargs(self, datetime, include=True):
        kwargs = self._start_kwargs(datetime, include=include)
        kwargs.update(self._end_kwargs(datetime, include=include))

        return kwargs

    def active_at_time(self, datetime_utc):
        kwargs = self._full_kwargs(datetime_utc, include=True)
        return self.filter(**kwargs)

    def inactive_at_time(self, datetime_utc):
        kwargs = self._full_kwargs(datetime_utc, include=True)
        return self.exclude(**kwargs)

    def past(self):
        now_utc = TimeHelper.get_utc_now_datetime()
        kwargs = self._end_kwargs(now_utc, include=False)
        return self.filter(**kwargs)

    def future(self):
        now_utc = TimeHelper.get_utc_now_datetime()
        kwargs = self._start_kwargs(now_utc, include=False)
        return self.filter(**kwargs)

    def active_now(self):
        now_utc = TimeHelper.get_utc_now_datetime()
        return self.active_at_time(now_utc)

    def inactive_now(self):
        now_utc = TimeHelper.get_utc_now_datetime()
        return self.inactive_at_time(now_utc)


class SoftDeleteQuerySet(models.query.QuerySet):
    '''
    QuerySet whose delete() does not delete items, but instead marks the
    rows as not active, and updates the timestamps
    '''

    def delete(self):
        utc_now = TimeHelper.get_utc_now_datetime()
        self.update(deleted_timestamp=utc_now)


class SoftDeleteAbstractMixin(TimeStampAbstractMixin):
    """
        This abstract mixin is an extension of the
        TimeStampAbstractMixin that adds a deleted_timestamp,
        and overrides the model
        delete method to prevent deletion of records.
    """

    TIMESTAMP_FIELDSETS = ('deleted_timestamp')
    # timestamps
    deleted_timestamp = models.DateTimeField(
        null=True, blank=True, db_index=True)

    def delete(self, *args, **kwargs):
        utc_now = TimeHelper.get_utc_now_datetime()
        self.deleted_timestamp = utc_now
        super(SoftDeleteAbstractMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
        This is a generic Manager that returns the queryset filtered by delted_timestamp=None
        based on self.alive_only attribute that defaults to True;
    """

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_timestamp=None)
        else:
            return SoftDeleteQuerySet(self.model, using=self._db)
