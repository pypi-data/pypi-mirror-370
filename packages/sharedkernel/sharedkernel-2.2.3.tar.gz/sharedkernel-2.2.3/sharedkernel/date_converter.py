import jdatetime
from datetime import datetime, timedelta
from persiantools.jdatetime import JalaliDate, JalaliDateTime
from math import floor

from sharedkernel.enum import ErrorCode

MONTH = 30


class DateConverter:
    @staticmethod
    def to_jalali(
        input_datetime: datetime | jdatetime.datetime, format_string: str = "%Y/%m/%d"
    ):
        if isinstance(input_datetime, jdatetime.datetime):
            return input_datetime.strftime(format_string)

        if isinstance(input_datetime, datetime):
            jalali_date = jdatetime.datetime.fromgregorian(date=input_datetime)
            return jalali_date.strftime(format_string)

        raise ValueError(ErrorCode.Unsupported_Date_Type)

    @staticmethod
    def to_georgian(
        input_datetime: datetime | jdatetime.datetime, format_string: str = "%Y/%m/%d"
    ):
        if isinstance(input_datetime, jdatetime.datetime):
            georgian_date = jdatetime.datetime.togregorian(input_datetime)
            return georgian_date.strftime(format_string)

        if isinstance(input_datetime, datetime):
            return input_datetime.strftime(format_string)

        raise ValueError(ErrorCode.Unsupported_Date_Type)

    @staticmethod
    def to_diff_persian_date_time_string(
        dt, comparison_base, append_hh_mm=False, has_suffix=False
    ):

        def get_persian_day_name(jalali_date):
            # Adjust this function based on how Persian day names should be retrieved
            day_names = [
                "شنبه",
                "یک‌شنبه",
                "دوشنبه",
                "سه‌شنبه",
                "چهارشنبه",
                "پنج‌شنبه",
                "جمعه",
            ]
            return day_names[jalali_date.weekday()]

        persian_date = JalaliDateTime.to_jalali(dt)
        persian_year = persian_date.year
        persian_month = persian_date.month
        persian_day = persian_date.day

        hour = dt.hour
        minute = dt.minute
        hh_mm = f"{hour:02}:{minute:02}"

        date = JalaliDateTime(persian_year, persian_month, persian_day, hour, minute)
        diff = date - comparison_base
        total_seconds = round(diff.total_seconds())
        total_days = round(total_seconds / 86400)
        total_hours = abs(round(total_seconds / 3600))
        total_months = abs(total_days // MONTH)  # Approximate months calculation

        suffix = " بعد"
        if total_seconds < 0:
            suffix = " قبل"
            total_seconds = abs(total_seconds)
            total_days = abs(total_days)
            total_months = abs(total_months)

        date_time_today = JalaliDateTime.to_jalali(comparison_base)
        yesterday = date_time_today - timedelta(days=1)
        tomorrow = date_time_today + timedelta(days=1)

        suffix = suffix if has_suffix else ""
        hh_mm = f"، ساعت {hh_mm}" if append_hh_mm else ""

        if total_hours < 24:
            if total_seconds < 60:
                return "هم اکنون"
            if total_seconds < 120:
                return f"یک دقیقه{suffix}{hh_mm}"
            if total_seconds < 3600:
                return f"{floor(total_seconds / 60)} دقیقه{suffix}{hh_mm}"
            if total_seconds < 7200:
                return f"یک ساعت{suffix}{hh_mm}"
            if total_seconds < 86400:
                return f"{floor(total_seconds / 3600)} ساعت{suffix}{hh_mm}"

        if yesterday.date() == date.date():
            return f"دیروز {get_persian_day_name(JalaliDate(yesterday.year, yesterday.month, yesterday.day))}"
        if tomorrow == date.date():
            return f"فردا {get_persian_day_name(JalaliDate(tomorrow.year, tomorrow.month, tomorrow.day))}"

        if total_days < MONTH:  # 30 days
            return f"{int(total_days)} روز{suffix}"

        total_months = int(total_days / MONTH)
        total_days = total_days - total_months * MONTH

        if total_months < 12:
            if total_days == 0:
                return f"{total_months} ماه {suffix}"
            else:
                return f"{total_months} ماه و {total_days} روز{suffix}"

        # Handling years and months
        total_years = total_months // 12
        remaining_months = total_months % 12
        if remaining_months > 0:
            return f"{total_years} سال و {remaining_months} ماه{suffix}"
        else:
            return f"{total_years} سال{suffix}"
