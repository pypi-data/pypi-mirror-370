
import argparse

from .errors import ValidationError
from .constants import (
    ENV_PARAM,
    EXPORT_DATA_PARAM,
    LAST_X_DAYS_PARAM,
    SEASON_YEAR,
    HANA_SEASON,
    FILE_NAME_PARAM,
    PREV_SEASONS_PARAM,
    SEND_EMAIL,
    MODEL_NAME_EXT,
    ALGO_TYPE
)


class Parameter:

    def get_value_or_else(self, value, default):
        return value or default

    def validate(self, value, default, required):
        pass

    def cast_value(self, value):
        pass


class EnvParameter(Parameter):

    def __init__(self) -> None:
        self.parameter_name = ENV_PARAM

    def validate(self, value, default, required):
        if not value:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )
        if value not in ['dev', 'stg', 'prd']:
            raise ValidationError(
                f"{self.parameter_name} available values: 'dev', 'stg', 'prd'"
            )

    def get_value_or_else(self, value, default):
        value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    def cast_value(self, value):
        return str(value)


class ExportDataParameter(Parameter):

    def __init__(self) -> None:
        self.parameter_name = EXPORT_DATA_PARAM

    def validate(self, value, default, required):
        if not value:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )
        if value not in ['True', 'False']:
            raise ValidationError(
                f"{self.parameter_name} available values: True/False"
            )

    def get_value_or_else(self, value, default):
        value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    # TODO: cast u boolean?
    def cast_value(self, value):
        return str(value)


class LastXDaysParameter(Parameter):
    def __init__(self) -> None:
        self.parameter_name = LAST_X_DAYS_PARAM

    def validate(self, value, default, required):
        if not value:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )
        if not value.isnumeric():
            raise ValidationError(
                f"Value of {self.parameter_name} must be a number"
            )

    def get_value_or_else(self, value, default):
        value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    def cast_value(self, value):
        return str(value)


class SeasonYearParameter(Parameter):
    def __init__(self) -> None:
        self.parameter_name = SEASON_YEAR

    def validate(self, value, default, required):
        if not value:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )
        if not value.isnumeric():
            raise ValidationError(
                f"Value of {self.parameter_name} must be a number"
            )

    def get_value_or_else(self, value, default):
        value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    def cast_value(self, value):
        return str(value)


class HanaSeasonParameter(Parameter):
    def __init__(self) -> None:
        self.parameter_name = HANA_SEASON
    def validate(self, value, default, required):
        if not value:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )
        if value not in ['WI', 'FA', 'SP', 'SU']:
            raise ValidationError(
                f"{self.parameter_name} available values: 'WI','SP','SU','FA'"
            )

    def get_value_or_else(self, value, default):
        value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    def cast_value(self, value):
        return str(value)


class FileNameParameter(Parameter):
    def __init__(self) -> None:
        self.parameter_name = FILE_NAME_PARAM

    def validate(self, value, default, required):
        if not value:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )
        if not isinstance(value, str):
            raise ValidationError(
                f"{self.parameter_name} should be the name of the file in string format"
            )

    def get_value_or_else(self, value, default):
        value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    def cast_value(self, value):
        return str(value)


class PreviousSeasonParameter(Parameter):
    def __init__(self) -> None:
        self.parameter_name = PREV_SEASONS_PARAM

    def validate(self, value, default, required):
        if not value:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )

    def get_value_or_else(self, value, default):
        value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    def cast_value(self, value):
        return int(value)


class SendEmailParameter(Parameter):
    def __init__(self) -> None:
        self.parameter_name = SEND_EMAIL

    def validate(self, value, default, required):
        if value is None:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )

    def get_value_or_else(self, value, default):
        if value is None:
            value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    def cast_value(self, value):
        return value


class ModelNameExt(Parameter):
    def __init__(self) -> None:
        self.parameter_name = MODEL_NAME_EXT

    def validate(self, value, default, required):
        if not value:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )

    def get_value_or_else(self, value, default):
        value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    def cast_value(self, value):
        return value


class AlgoTypeParameter(Parameter):
    def __init__(self) -> None:
        self.parameter_name = ALGO_TYPE

    def validate(self, value, default, required):
        if not value:
            value = default
        if not value and required:
            raise ValidationError(
                f"Parameter is required: {self.parameter_name}"
            )

    def get_value_or_else(self, value, default):
        value = super().get_value_or_else(value, default)
        return self.cast_value(value)

    def cast_value(self, value):
        return value

def gather_parameters():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        f"--{ENV_PARAM}",
        help="environment in which job is running",
    )

    parser.add_argument(
        f"--{EXPORT_DATA_PARAM}",
        help="save data parameter",
    )

    parser.add_argument(
        f"--{LAST_X_DAYS_PARAM}",
        help="parameter to determine the number of days taken into account in query",
    )

    parser.add_argument(
        f"--{SEASON_YEAR}",
        help="parameter to determine the current season year",
    )

    parser.add_argument(
        f"--{HANA_SEASON}",
        help="parameter to determine the current Hana season",
    )

    parser.add_argument(
        f"--{FILE_NAME_PARAM}",
        help="file name parameter",
    )

    parser.add_argument(
        f"--{PREV_SEASONS_PARAM}",
        help="number of previous seasons to consider",
    )

    parser.add_argument(
        f"--{SEND_EMAIL}",
        action="store_false",
        help="DO NOT send out email with link to download file",
    )

    parser.add_argument(
        f"--{MODEL_NAME_EXT}",
        help="suffix to append to model name",
    )

    parser.add_argument(
        f"--{ALGO_TYPE}",
        help="algo type for carton conversion forecasting: 'PC' or 'VF'",
    )

    args = parser.parse_args()
    params_dictionary = vars(args)

    return params_dictionary
