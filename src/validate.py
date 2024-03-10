import re

def is_not_blank(string):
    if bool(string and not string.isspace()) == False:
        raise ValueError('Validation failed: String is empty')
    return True

def is_date(date_string):
    # Example: 1/9/2024
    pattern = r"^(1[0-2]|[1-9])/([1-9]|[12][0-9]|3[01])/\d{4}$"

    if not re.match(pattern, date_string):
        raise ValueError('Validation failed: Invalid date format: ' + str(date_string))
    return True

def is_date_novus(date_string):
    # Example: 01/09/24
    pattern = r"^(0[1-9]|1[0-2])/(0[1-9]|1[0-9]|2[0-9]|3[0-1])/\d{2}$"

    if not re.match(pattern, date_string):
        raise ValueError('Validation failed: Invalid date format: ' + str(date_string))
    return True

def is_time(time_string):
    # Example: 9:01 PM
    pattern = r"^(1[0-2]|[1-9]):([0-5][0-9]) (AM|PM)$"

    if not re.match(pattern, time_string):
        raise ValueError('Validation failed: Invalid time format: ' + str(time_string))
    return True

def is_boolean(my_var):
    if not isinstance(my_var, bool):
        raise ValueError('Validation failed: Type is not a boolean: ' + str(my_var))
    return True

def is_string(my_var):
    if not isinstance(my_var, str):
        raise ValueError('Validation failed: Type is not a string: ' + str(my_var))
    return True

def is_int(my_var):
    if not isinstance(my_var, int):
        raise ValueError('Validation failed: Type is not an integer: ' + str(my_var))
    return True