import datetime


def age(dob):
    today = datetime.date.today()
    years = today.year - dob.year

    try:
        birthday = datetime.date(today.year, dob.month, dob.day)
    except ValueError as e:
        if dob.month == 2 and dob.day == 29:
            birthday = datetime.date(today.year, 3, 1)
        else:
            raise e
    if today < birthday:
        years -= 1
    return years
