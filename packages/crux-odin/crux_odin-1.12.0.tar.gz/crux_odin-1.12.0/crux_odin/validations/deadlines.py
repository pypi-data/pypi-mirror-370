from typing import Callable, Optional

from crux_odin.validations.valid_timezones import VALID_TIMEZONES


def default_cron_validation(
    cron_element: str,
    lower_bound: int,
    upper_bound: int,
    cron_element_label: str,
    *args,
    asterisk_allowed: bool = True,
    extra_validation: Callable = None,
):
    if asterisk_allowed and cron_element == "*":
        return cron_element

    if extra_validation and extra_validation(cron_element, *args):
        return cron_element

    try:
        cron_element_int = int(cron_element)

        if cron_element_int < lower_bound or cron_element_int > upper_bound:
            raise ValueError(
                f"{cron_element_label} must be between {lower_bound}-{upper_bound}"
            )
    except ValueError:
        raise ValueError(f"{cron_element_label} is not a valid value")

    return cron_element


def deadline_minute_validation(deadline_minute: str):
    return default_cron_validation(
        deadline_minute, 0, 59, "Deadline minute", asterisk_allowed=False
    )


def deadline_hour_validation(deadline_hour: str):
    return default_cron_validation(deadline_hour, 0, 23, "Deadline hour")


def _validate_weekday_expression(deadline_day_of_the_month: str) -> bool:
    if deadline_day_of_the_month == "*W":
        return True

    if deadline_day_of_the_month.endswith("W"):
        try:
            day_of_month_value = int(deadline_day_of_the_month[:-1])

            if day_of_month_value < 1 or day_of_month_value > 31:
                raise ValueError("Deadline day of month must be between 1-31")

            return True
        except ValueError:
            raise ValueError("Deadline day of month is not a valid value")

    return False


def _validate_cron_interval(
    expression: str, lower_bound: int, upper_bound: int
) -> bool:
    if "-" in expression:
        try:
            split_expression = expression.split("-")

            if len(split_expression) != 2:
                raise ValueError(f"Invalid cron interval expression: {expression}")

            lower_input = int(split_expression[0])
            upper_input = int(split_expression[1])

            if (
                lower_input < lower_bound
                or upper_input > upper_bound
                or lower_input >= upper_input
            ):
                raise ValueError(
                    f"Expression {expression} must be a valid bound between "
                    f"{lower_bound}-{upper_bound}"
                )

            return True
        except ValueError:
            raise ValueError(f"Invalid cron interval expression: {expression}")

    return False


def deadline_day_of_the_month_validation(deadline_day_of_the_month: str):
    return default_cron_validation(
        deadline_day_of_the_month,
        1,
        31,
        "Deadline day of month",
        extra_validation=_validate_weekday_expression,
    )


def deadline_month_validation(deadline_month: str):
    return default_cron_validation(deadline_month, 1, 12, "Deadline month")


def deadline_day_of_week_validation(deadline_day_of_week: str):
    return default_cron_validation(
        deadline_day_of_week,
        0,
        6,
        "Deadline day of week",
        0,
        6,
        extra_validation=_validate_cron_interval,
    )


def deadline_year_validation(deadline_year):
    if deadline_year != "*":
        raise ValueError("Currently the deadline year must be *")

    return deadline_year


def timezone_validation(timezone: Optional[str] = None):
    if timezone and timezone not in VALID_TIMEZONES:
        raise ValueError(f"Invalid timezone: {timezone}")

    return timezone


def file_frequency_validation(file_frequency: str):
    if file_frequency not in [
        "intraday",
        "daily",
        "weekly",
        "bi-weekly",
        "monthly",
        "quarterly",
        "semi-annual",
        "yearly",
    ]:
        raise ValueError(f"Invalid file frequency: {file_frequency}")

    return file_frequency
