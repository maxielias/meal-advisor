import asyncio
import logging
import sys
import re
from typing import IO
import aiofiles
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import pandas as pd
import json
from dateutil.parser import parse


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True


def change_symbols_in_column_names(df):
    df_cols = df.columns
    df_new_cols = ["".join(re.sub("[^0-9a-zA-Z]+", " ", c).split(" ")[0]+re.sub("[^0-9a-zA-Z]+", " ", c).split(" ")[1].capitalize()) if re.search("[^0-9a-zA-Z]+", c) else c for c in df_cols]
    print(df_new_cols)
    return df_new_cols


if __name__ == "__main__":
    import pathlib
    import sys

    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    here = pathlib.Path(__file__).parent

    outpath = here.joinpath("data/recipes_raw.json")
    with open(outpath, "r", encoding="utf-8") as jsonfile:
        jsondata = json.loads(jsonfile.read())

    df_raw = pd.read_json(outpath)
    df_flattened = pd.json_normalize(jsondata, record_path =['recipe'][0])
    df = pd.concat([df_raw, df_flattened], axis=1).drop(columns=["recipe"]).reset_index().drop(columns="index")

    print(change_symbols_in_column_names(df))

    #asyncio.run(write_file(file=outpath, urls=category_meal_link["link"]))