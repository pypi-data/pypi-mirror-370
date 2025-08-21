from datetime import datetime, timezone
import re

dt_format_sec_fract = "%Y-%m-%d %H:%M:%S.%f"
dt_format_sec_int = "%Y-%m-%d %H:%M:%S"


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
            return out
        except Exception as e:
            f_name = func.__name__
            exc = f'{f_name} --> {str(e)}'
            raise Exception(exc)
    return wrapper


@catch_exception
def clean_string(txt):
    out = txt.replace(r"\n", " ").replace("'", " ")
    out = re.sub(r"\s+", " ", out)
    return out.strip()


@catch_exception
def remove_special_characters(txt):
    special_chs = r"""!@#$%^&*()'[]{};:,./<>?\|`"~-=_+÷þ–—‘’“”•€►👍😁😂😉😜😬£¨©ª«°²´¹º»¿×ß"""
    out = txt.replace(r"\n", " ")
    out = out.translate({ord(c): " " for c in special_chs})
    out = re.sub(r"\s+", " ", out)
    return out.strip()


@catch_exception
def get_time_now(sec_fractions=True):
    dt_format = dt_format_sec_fract if sec_fractions else dt_format_sec_int
    return datetime.now(timezone.utc).astimezone().strftime(dt_format)


@catch_exception
def str_to_datetime(tmp_str):
    dt_format = dt_format_sec_fract if '.' in tmp_str else dt_format_sec_int
    return datetime.strptime(tmp_str, dt_format)


@catch_exception
def datetime_to_str(dt):
    dt_format = dt_format_sec_fract if bool(dt.microsecond) else dt_format_sec_int
    return dt.strftime(dt_format)


@catch_exception
def validate_time(tmp_str):
    dt_format = dt_format_sec_fract if '.' in tmp_str else dt_format_sec_int
    try:
        datetime.strptime(tmp_str, dt_format)
        return True
    except ValueError:
        return False


@catch_exception
def get_elapsed_seconds(dt_end_str, dt_start_str, round_d=3):
    return round((str_to_datetime(dt_end_str) - str_to_datetime(dt_start_str)).total_seconds(), round_d)
