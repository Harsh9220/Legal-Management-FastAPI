from datetime import datetime, date


class DateHelper:

    # Date Formats
    db_date_format = "%Y-%m-%d"

    # Convert string to date
    def string_to_date(date: str, date_format: str = db_date_format):
        return datetime.strptime(date, date_format).date()
