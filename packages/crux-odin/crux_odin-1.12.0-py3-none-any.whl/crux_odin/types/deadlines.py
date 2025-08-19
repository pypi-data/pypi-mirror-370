from enum import Enum
from typing_extensions import Annotated
from crux_odin.validations.deadlines import (
    deadline_minute_validation,
    deadline_hour_validation,
    deadline_day_of_the_month_validation,
    deadline_month_validation,
    deadline_day_of_week_validation,
    deadline_year_validation,
    file_frequency_validation,
    timezone_validation,
)
from pydantic.functional_validators import PlainValidator
from typing import Literal


DeadlineMinute = Annotated[str, PlainValidator(deadline_minute_validation)]
DeadlineHour = Annotated[str, PlainValidator(deadline_hour_validation)]
DeadlineDayOfMonth = Annotated[
    str, PlainValidator(deadline_day_of_the_month_validation)
]
DeadlineMonth = Annotated[str, PlainValidator(deadline_month_validation)]
DeadlineDayOfWeek = Annotated[str, PlainValidator(deadline_day_of_week_validation)]
DeadlineYear = Annotated[str, PlainValidator(deadline_year_validation)]
FileFrequency = Annotated[str, PlainValidator(file_frequency_validation)]
Timezone = Annotated[str, PlainValidator(timezone_validation)]
