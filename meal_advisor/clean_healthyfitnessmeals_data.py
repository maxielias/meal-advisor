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
    rep_list = []
    for i,j in enumerate(df_new_cols):
        if j in rep_list:
            j = f"{j}{i}"
            df_new_cols[i] = j
        else:
            rep_list.append(j)
    
    return df_new_cols

def servings_to_int(df, col:str):
    # servings = [d["servings"] for i in range(len(df)) for d in df[i]["recipe"]]
    servings = [s for s in df[col]]
    serving_list = list()
    for s in servings:
        try:
            if "-" in s:
                split_s = [int(i) for i in re.findall(r'\d+', s)]
                avg_serving =  int(round(sum(split_s) / len(split_s), 0))
                serving_list.append(avg_serving)
            else:
                serving_list.append(int(re.findall(r'\d+', s)[0]))
        except:
            serving_list.append(s)

    return serving_list


def calories_to_int(df, col:str):
    calories = [c for c in df[col]]
    calorie_list = list()
    for c in calories:
        try:
            if isinstance(c, float):
                calorie_list.append(c) #int(re.findall(r'\d+', c)[0]))
            elif isinstance(c, str):
                isnum = float("".join([n for n in c if n.isdigit()]))
                calorie_list.append(isnum)
        except Exception as e:
            print(e)
            calorie_list.append(c)

    return calorie_list


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
    df.columns = change_symbols_in_column_names(df)
    df["servings"] = servings_to_int(df, "servings")
    df["calories"] = calories_to_int(df, "calories")


    print(df.to_json)

    outpath = here.joinpath("data/recipes_clean_healthyfitnessmeals.json")
    with open(outpath, "w", encoding="utf-8") as jsonfile:
        jsonfile = json.dumps(df.to_json, indent=4)