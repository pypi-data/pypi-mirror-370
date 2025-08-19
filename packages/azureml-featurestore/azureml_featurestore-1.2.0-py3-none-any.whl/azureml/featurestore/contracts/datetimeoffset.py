# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from datetime import timedelta

from azure.ai.ml._utils.utils import dump_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from marshmallow import EXCLUDE


class DateTimeOffset(object):
    """Class representing any time offsets"""

    def __init__(self, days: int = None, hours: int = None, minutes: int = None):
        if days is None and hours is None and minutes is None:
            raise ValueError("At least one of days, hours or minutes must be specified")
        self.days = days if days else 0
        self.hours = hours if hours else 0
        self.minutes = minutes if minutes else 0
        if self.days < 0 or self.hours < 0 or self.minutes < 0:
            raise ValueError("Negative values are not allowed")

    def __repr__(self):
        yaml_serialized = self._to_dict()
        return dump_yaml(yaml_serialized, default_flow_style=False)

    def __str__(self):
        return self.__repr__()

    def _to_dict(self):
        from azureml.featurestore.schema.feature_set_schema import DateTimeOffsetSchema

        return DateTimeOffsetSchema(unknown=EXCLUDE, context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DateTimeOffset):
            return self.days == other.days and self.hours == other.hours and self.minutes == other.minutes
        return False

    def to_timedelta(self):
        return timedelta(days=self.days, hours=self.hours, minutes=self.minutes)

    def to_minutes(self):
        return self.days * 24 * 60 + self.hours * 60 + self.minutes

    def to_feathr_window(self) -> str:
        if self.minutes:
            hours_in_minutes = self.hours * 60 if self.hours else 0
            days_in_minutes = self.days * 24 * 60 if self.days else 0
            window = self.minutes + hours_in_minutes + days_in_minutes
            return f"{window}m"
        if self.hours:
            days_in_hours = self.days * 24 if self.days else 0
            window = self.hours + days_in_hours
            return f"{window}h"
        if self.days:
            return f"{self.days}d"
