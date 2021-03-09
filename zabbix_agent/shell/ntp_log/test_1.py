import datetime

this_month = datetime.datetime.now().strftime('%Y-%m')
print(this_month)
bid_day = this_month + '-25'


def check_weekend(i):
    i = datetime.datetime.strptime(i, '%Y-%m-%d')
    i_weekday = i.isoweekday()
    if i_weekday < 6:
        return i
    else:
        while i_weekday > 6:
            i = i + datetime.timedelta(days=1)
            i_weekday = i.isoweekday()
        return i


bid_day = str(check_weekend(bid_day)).split(' ')[0]
print(bid_day)

today_date = datetime.datetime.today()
today_date = str(today_date).split(' ')[0]
print(today_date)

if today_date == bid_day:
    print(1)
else:
    print(2)
