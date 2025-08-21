import datetime

from mb_cruise_migration.framework.consts.date_consts import ORM_ISO_DATE_FORMAT


def dict_value_or_none(dictionary, key):
    return dictionary[key] if key in dictionary else None


def multiple_values_in_survey_instrument(survey_instrument) -> bool:
    instruments = survey_instrument.split(";")
    return len(instruments) != 1


def strip_none(may_have_nones: list):
    return [item for item in may_have_nones if item is not None]


def strip_special_chars(string: str):
    return "".join(char for char in string if char.isalnum())


def normalize_date(date_field_value, date_field_name=None) -> str:
    """
    normalizes datetime.datetime or an iso formatted string to an iso formatted
    string sans microseconds that is expected by CRUISE ORM
    """
    if date_field_value is None or not date_field_value:
        return ""

    date_field_type = type(date_field_value)

    if date_field_type == str:
        try:
            return datetime.datetime.fromisoformat(date_field_value).strftime(
                ORM_ISO_DATE_FORMAT
            )
        except ValueError:
            raise ValueError(
                "Date string for "
                + date_field_value
                + " did not match expected iso format for field "
                + date_field_name
            )

    if date_field_type == datetime or date_field_type == datetime.datetime:
        return date_field_value.strftime(ORM_ISO_DATE_FORMAT)

    raise ValueError(
        "date field "
        + date_field_name
        + " contained unsupported type: "
        + str(type(date_field_value))
    )
