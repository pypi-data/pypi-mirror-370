###############################################################################
#
# (C) Copyright 2020 Maikon Araujo
#
# This is an unpublished work containing confidential and proprietary
# information of Maikon Araujo. Disclosure, use, or reproduction
# without authorization of Maikon Araujo is prohibited.
#
###############################################################################
import numpy as np
from quant import calendars # type: ignore
import datetime


def init_cal(s_year: int, e_year: int) -> np.busdaycalendar:
    h = calendars.generate("b3", s_year, e_year)
    return np.busdaycalendar(holidays=h)


def str2date(dstr: str) -> datetime.date:
    return datetime.datetime.strptime(dstr, "%y%m%d").date()


def date2b3str(d: datetime.date) -> str:
    return d.strftime("%y%m%d")


def date_range(dates: str | None) -> np.ndarray:
    if dates is None:
        return np.array([datetime.date.today()])

    ds = dates.split(",")
    if len(ds) < 2:
        return np.array([])

    dr = list(map(str2date, ds))
    years = [d.year for d in dr]
    cal = init_cal(years[0], years[1] + 1)
    n = np.busday_count(dr[0], dr[1], busdaycal=cal) + 1
    return np.array(
        [np.busday_offset(dr[0], i, busdaycal=cal, roll="forward") for i in range(n)]
    ).astype(datetime.date)


import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="Parse range", description="Parse range")

    parser.add_argument("-r", "--range")

    args = parser.parse_args()

    print(date_range(args.range))
