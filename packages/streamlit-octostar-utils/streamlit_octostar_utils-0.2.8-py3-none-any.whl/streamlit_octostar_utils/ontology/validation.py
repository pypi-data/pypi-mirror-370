from ..core.timestamp import string_to_datetime


def validate_and_format_timbr_type(timbr_type, value):
    def _check_boolean(x):
        if str(x).lower() not in ["true", "false", "0", "1"]:
            return ValueError()
        return x

    def _check_date(x):
        return string_to_datetime(x).strftime("%Y-%m-%dT%H:%M:%SZ")

    timbr_type_to_op = {
        "string": lambda x: str(x),
        "integer": lambda x: int(x),
        "smallint": lambda x: int(x),
        "bigint": lambda x: int(x),
        "decimal": lambda x: float(x),
        "float": lambda x: float(x),
        "double": lambda x: float(x),
        "boolean": lambda x: _check_boolean(x),
        "date": lambda x: _check_date(x),
        "timestamp": lambda x: _check_date(x),
    }
    assert timbr_type in timbr_type_to_op
    if value is None:
        return value
    else:
        try:
            value = timbr_type_to_op[timbr_type](value)
        except:
            raise ValueError("Validation failed!")
        return value
