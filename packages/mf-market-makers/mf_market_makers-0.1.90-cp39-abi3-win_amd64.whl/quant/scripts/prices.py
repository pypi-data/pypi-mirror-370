###############################################################################
#
# (C) Copyright 2020 Maikon Araujo
#
# This is an unpublished work containing confidential and proprietary
# information of Maikon Araujo. Disclosure, use, or reproduction
# without authorization of Maikon Araujo is prohibited.
#
###############################################################################
import argparse
from time import sleep
import requests
import subprocess
import os
import logging
import zipfile

from dotenv import load_dotenv
from quant.scripts.date_range import date_range, date2b3str
from quant.b3xml import instruments_to_csv, prices_to_csv, prices_to_mssql  # type: ignore


def download(url: str, file: str, proxy, retry=5, time_btw_retries=5):
    try:
        with requests.get(url, stream=True, proxies=proxy) as r:
            r.raise_for_status()
            with open(file, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:
        if retry == 0:
            raise e
        logging.warning(
            f"Failled to download file, retrying {retry} more times after {time_btw_retries} secs."
        )
        sleep(time_btw_retries)
        download(url, file, proxy, retry=retry - 1, time_btw_retries=time_btw_retries * 2)


def unzip(zip_file: str):
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(".")

    os.remove(zip_file)


"https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"
TASK = {
    "prices": {
        # "url": "http://www.bmf.com.br/Ftp/IPN/TRS/BVBG.086.01/PR{}.zip",
        "url": "https://www.b3.com.br/pesquisapregao/download?filelist=PR{}.zip,",
        "zip_file": "PR{}.zip",
        "csv_file": "PR{}_{}.csv",
        "to_csv_fun": prices_to_csv,
        "unzip": True,
        "tables": ["b3_prices"],
    },
    "instruments": {
        # "url": "http://www.bmf.com.br/Ftp/IPN/TS/BVBG.028.02/IN{}.zip",
        "url": "https://www.b3.com.br/pesquisapregao/download?filelist=IN{}.zip,",
        "zip_file": "IN{}.zip",
        "csv_file": "IN{}_{}.csv",
        "to_csv_fun": instruments_to_csv,
        "unzip": True,
        "tables": ["equity", "opt_on_equity", "future", "opt_spot_future"],
    },
}


def postgress_execution(csv_file_fmt, to_csv_fun, dstr, file_zip, tbl):
    file_csv = csv_file_fmt.format(dstr, tbl)
    logging.info(f"making -> {file_csv}")

    to_csv_fun(file_zip, tbl, file_csv)

    logging.info(f"psql -> {file_csv}")
    subprocess.run(
        [
            "psql",
            "-c",
            f"\\copy {tbl} from {file_csv} csv header encoding 'UTF-8'",
            "-U",
            "postgres",
            "market_data_db",
        ]
    )
    logging.info(f"removing -> {file_csv}")
    os.remove(file_csv)


def mssql_execution(file_zip, tbl):

    server = os.environ.get("MS_DB_SERVER")
    port = os.environ.get("MS_DB_PORT")
    user = os.environ.get("MS_DB_USER")
    pwd = os.environ.get("MS_DB_PWD")
    database = os.environ.get("MS_DB_DATABASE")
    if not server:
        raise Exception("missing MS_DB_SERVER env.")
    if not port:
        raise Exception("missing MS_DB_PORT env.")
    if not user:
        raise Exception("missing MS_DB_USER env.")
    if not pwd:
        raise Exception("missing MS_DB_PWD env.")
    if not database:
        raise Exception("missing MS_DB_DATABASE env.")

    logging.info(f"uploading {file_zip} -> {tbl}")
    prices_to_mssql(file_zip, user, pwd, server, int(port), tbl, database)
    logging.info(f"uploading {file_zip} -> {tbl} - done!")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s")

    load_dotenv()

    proxy_url = os.environ.get("APP_PROXY")
    proxy = None
    if proxy_url is not None:
        proxy = {
            "http": f"{proxy_url}",
            "https": f"{proxy_url}",
        }


    parser = argparse.ArgumentParser(
        prog="Prices",
        description="Download daily prices files from b3 PRYYMMDD.zip, parse it and upgrade to database",
    )

    parser.add_argument("task", choices=["prices", "instruments"])
    parser.add_argument("-r", "--range")
    parser.add_argument(
        "--dry-run", action="store_true", help="only prints the list of dates and exit"
    )

    parser.add_argument("--dest", default="postgres", choices=["postgres", "mssql"])

    args = parser.parse_args()

    if args.dry_run:
        print(args)
        print(date_range(args.range))
        exit()

    url_fmt = TASK[args.task]["url"]
    zip_file_fmt = TASK[args.task]["zip_file"]
    csv_file_fmt = TASK[args.task]["csv_file"]
    to_csv_fun = TASK[args.task]["to_csv_fun"]
    tables = TASK[args.task]["tables"]
    to_unzip = TASK[args.task]["unzip"]
    dest = args.dest

    for d in date_range(args.range):
        dstr = date2b3str(d)
        url = url_fmt.format(dstr)
        file_zip = zip_file_fmt.format(dstr)
        file_zip = f"orig_{file_zip}" if to_unzip else file_zip
        try:
            logging.info(f"downloading -> {file_zip}")
            download(url, file_zip, proxy)
            logging.info(f"downloaded -> {file_zip}")

            if to_unzip:
                unzip(file_zip)
                file_zip = file_zip[5:]

            if dest == "postgres":
                for tbl in tables:
                    postgress_execution(csv_file_fmt, to_csv_fun, dstr, file_zip, tbl)
            else:
                for tbl in tables:
                    mssql_execution(file_zip, tbl)

            logging.info(f"removing -> {file_zip}")
            os.remove(file_zip)
        except Exception as ex:
            logging.error(f"Error: {d} {ex}")
