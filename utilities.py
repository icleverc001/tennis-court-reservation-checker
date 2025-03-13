import datetime
import calendar

def get_limit_date(thresholdDay: int) -> datetime.date:
    # Table操作
    dateToday: datetime.date = datetime.date.today()
    thismonthdates: int = calendar.monthrange(dateToday.year, dateToday.month)[1]
    limitData: datetime.date = datetime.date(dateToday.year, dateToday.month, thismonthdates)
    if dateToday.day >= thresholdDay:
        nextmonthdate: datetime.date = limitData + datetime.timedelta(days=1)
        # limitData = nextmonthdate.replace(day=calendar.monthrange(nextmonthdate.year, nextmonthdate.month)[1], hour=23, minute=59, second=59)
        limitData = nextmonthdate.replace(day=calendar.monthrange(nextmonthdate.year, nextmonthdate.month)[1])

    return limitData