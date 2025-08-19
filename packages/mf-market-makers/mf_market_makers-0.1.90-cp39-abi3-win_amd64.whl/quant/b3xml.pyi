###############################################################################
#
# (C) Copyright 2020 Maikon Araujo
#
# This is an unpublished work containing confidential and proprietary
# information of Maikon Araujo. Disclosure, use, or reproduction
# without authorization of Maikon Araujo is prohibited.
#
###############################################################################

import datetime as dt

def instruments_to_csv(fname: str, ftype: str, dest_file: str): ...
def prices_to_csv(fname: str, ftype: str, dest_file: str): ...
def prices_to_mssql(
    fname: str, user: str, pwd: str, host: str, port: int, table: str, database: str
): ...
def ibov_w_to_postgres(
    dbrl: str,
    ref_date: dt.date,
    divisor: float,
    ticker_symbol: list[str],
    quantity: list[int],
): ...
def ibov_w_to_mssql(
    user: str,
    pwd: str,
    host: str,
    port: int,
    database: str,
    ref_date: dt.date,
    divisor: float,
    ticker_symbol: list[str],
    quantity: list[int],
): ...

def load_imbarq(imb_type: str, zip_file: str, db_file: str): ...
