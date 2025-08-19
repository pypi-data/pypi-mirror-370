# expiration_checker.py

import datetime


def is_software_expired():
    expiration_date = datetime.date(2025, 4, 11)
    current_date = datetime.date.today()

    if current_date >= expiration_date:
        return True,expiration_date
    else:
        return False,expiration_date
