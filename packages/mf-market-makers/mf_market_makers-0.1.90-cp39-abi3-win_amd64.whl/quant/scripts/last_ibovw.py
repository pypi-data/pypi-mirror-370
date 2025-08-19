import json
import datetime as dt
from base64 import b64encode
import requests
from time import sleep
import logging
import argparse
from dotenv import load_dotenv
import os
from quant.b3xml import ibov_w_to_postgres, ibov_w_to_mssql  # type ignore


IBOV_URL = (
    "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay"
)
IBOV_QUERY_STR = (
    b'{"language":"pt-br","pageNumber":1,"pageSize":200,"index":"IBOV","segment":"1"}'
)


def download_ibov_w(proxy,
    retry=5, time_btw_retries=5
) -> tuple[dt.date, float, list[str], list[int]]:
    def fmt(s: str):
        return s.replace(".", "").replace(",", ".")

    def to_date(s: str) -> dt.date:
        return dt.datetime.strptime(s, "%d/%m/%y").date()

    try:
        with requests.get(
            f'{IBOV_URL}/{b64encode(IBOV_QUERY_STR).decode("utf-8")}', proxies=proxy
        ) as r:
            r.raise_for_status()
            obj = json.loads(r.content)
            reductor = float(fmt(obj["header"]["reductor"]))
            date_ref = to_date(obj["header"]["date"])
            ticket_symbol = [e["cod"] for e in obj["results"]]
            quantity = [int(fmt(e["theoricalQty"])) for e in obj["results"]]
            return (date_ref, reductor, ticket_symbol, quantity)

    except Exception as e:
        if retry == 0:
            raise e
        logging.warning(
            f"Failled to download IBOV file, retrying {retry} more times after {time_btw_retries} secs."
        )
        sleep(time_btw_retries)
        return download_ibov_w(proxy, retry=retry - 1, time_btw_retries=time_btw_retries * 2)


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
        prog="Ibov Weights",
        description="Download ibov weights from b3 and upgrade to database",
    )

    parser.add_argument("--dest", default="postgres", choices=["postgres", "mssql"])

    args = parser.parse_args()
    dest = args.dest

    logging.info("Query B3 for Ibov composition")
    (date_ref, divisor, ticket_symbol, quantity) = download_ibov_w(proxy)
    logging.info(f"Found {date_ref} with {len(quantity)} symbols and divisor = {divisor}")
  
    
    if dest == "postgres":
        url = os.environ["DATABASE_URL"]
        ibov_w_to_postgres(url, date_ref, divisor, ticket_symbol, quantity)
        logging.info(f"Records inserted.")
    else:
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

        logging.info(f"uploading ibovw -> {database}")
        ibov_w_to_mssql(user, pwd, server, int(port),  database, date_ref, divisor, ticket_symbol, quantity)
        logging.info(f"uploading ibovw -> {database} done!")

        
