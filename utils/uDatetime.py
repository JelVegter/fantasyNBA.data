from datetime import date, datetime, timedelta
from dateutil import parser

TODAY = date.today().strftime("%Y%m%d")
ONE_DAYS_AGO = (datetime.now() + timedelta(days=-1)).strftime("%Y%m%d")
THREE_DAYS_AGO = (datetime.now() + timedelta(days=-3)).strftime("%Y%m%d")
NOW = datetime.now().strftime("%Y%m%d%H%M%S")


def convert_date(date, hyphens: bool = False):
    date = parser.parse(date)
    if hyphens is False:
        return datetime.strftime(date, "%Y%m%d")
    return datetime.strftime(date, "%Y-%m-%d")
