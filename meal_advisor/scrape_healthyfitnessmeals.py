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


def transform_recipe_healthyfitness(bs):
    """
    """
    data_dict = dict()

    # Title
    try:
        title = bs.find("h2").get_text()
        data_dict["title"] = title
    except Exception as e:
        print("Title")
        print(e)
        pass
    
    
    # Description
    try:
        description = bs.find("div", class_="wprm-recipe-summary").get_text()
        data_dict["description"] = description
    except Exception as e:
        print("Description")
        print(e)
        pass
    
    # Image
    try:
        imgsrc = bs.find("img")["srcset"]
        data_dict["image"] = imgsrc
    except:
        try:
            imgsrc = bs.find("img")["data-lazy-srcset"]
            data_dict["image"] = imgsrc
        except Exception as e:
            print("Image source not found")
            # print(e)
            pass
    
    # Additional information
    misc_data = bs.find_all("div", class_="wprm-recipe-block-container")
    for c in misc_data:
        try:
            c_split = c.get_text().split(":")
        
            # Joining two word keys:
            if len(c_split[0].split(" ")) > 1:
                dict_key = re.sub("[^0-9a-zA-Z]+", "", c_split[0].split(" ")[0]).lower()+c_split[0].split(" ")[1].strip().capitalize()
                dict_item = c_split[1].lower().strip()
                data_dict[dict_key] = dict_item
            # If key is only one word:
            else:
                dict_key = c_split[0].lower().strip()
                dict_item = c_split[1].lower().strip()
                data_dict[dict_key] = dict_item
        except Exception as e:
            print("Additional information")
            print(e)
            pass

    # Ingredients
    try:
        items = list()
        units = list()
        amount = list()
        it = bs.find_all("span", class_="wprm-recipe-ingredient-name")
        un = bs.find_all("span", class_="wprm-recipe-ingredient-unit")
        am = bs.find_all("span", class_="wprm-recipe-ingredient-amount")
        for i in range(len(it)):
            try:
                amount.append(am[i].get_text().lower())
            except:
                amount.append("1")
                pass
            try:
                units.append(un[i].get_text().lower())
            except:
                units.append("units")
                pass
            try:
                items.append(it[i].get_text().lower())
            except:
                items.append("unknown-ingredient")
                pass
        data_dict["ingredients"] = {"item": items, "amount": amount, "unit": units}
    except Exception as e:
        print("Ingredients")
        print(e)
        pass

    # Instructions
    try:
        instructions = bs.find("ul", class_="wprm-recipe-instructions").get_text() #.find("div", class_="wprm-recipe-summary")) #.find("h2"))
        data_dict["instructions"] = instructions
    except Exception as e:
        print("Instructions")
        print(e)
        pass
    
    # Notes
    try:
        notes = bs.find("div", class_="wprm-recipe-notes").get_text() #.find("div", class_="wprm-recipe-summary")) #.find("h2"))
        data_dict["notes"] = notes
    except Exception as e:
        notes = ""
        data_dict["notes"] = notes
        print("Notes")
        print(e)

    return data_dict


async def fetch_url(url: str, session: ClientSession, **kwargs) -> str:
    """GET request wrapper to fetch page HTML.
    kwargs are passed to 'session.request()'.
    """
    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    logger.info("Got session response [%s] for URL: %s", resp.status, url)
    html = await resp.text()
    # await asyncio.sleep(1)

    return html


async def parse(url: str, session: ClientSession, **kwargs) -> set:
    """Find HREFs in the HTML of 'url'."""
    data = dict()
    category = category_meal_link.loc[category_meal_link["link"]==url, "category"].values[0]

    try:
        resp = await fetch_url(url=url, session=session, **kwargs)
        soup = BeautifulSoup(resp, "html.parser")
    except (
        aiohttp.ClientError,
        aiohttp.http_exceptions.HttpProcessingError,
    ) as e:
        logger.error(
            "aiohttp exception for %s [%s]: %s",
            url,
            getattr(e, "status", None),
            getattr(e, "message", None),
        )
        logger.debug(e)
        return data
    except Exception as e:
        logger.exception(
            "Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {})
        )
        return data
    else:
        try:
            bs = soup.find("div", class_="wprm-recipe-container")
            data_dict = transform_recipe_healthyfitness(bs)
            # logger.debug(bs)
            # data.append([f'{url},{category_meal_link["category"].loc[category_meal_link["link"]==url].item()},{bs}'])
            # logger.debug(data)
            # category = category_meal_link["category"].loc[category_meal_link["link"]==url]
            # data = [{"url": url, "category": category, "recipe": data_dict}]
            data["url"] = url
            data["category"] = category
            data["recipe"] = [data_dict]
            
            return data

        except Exception as e:
            #print(category)
            logger.debug(e)
            return data


async def parse_to_file(file: IO, url: str, **kwargs) -> None:
    """Write the found HREFs from 'url' to 'file'."""
    res = await parse(url=url, **kwargs)
    if not res:
        return None

    '''async with aiofiles.open(file, "r", "encoding=utf8") as f:
        last_line = len(file.readlines())'''
    async with aiofiles.open(file, "a", encoding="utf-8") as f:
        try:
            if res["url"]:
                json_to_write = json.dumps(res, indent=4)
                await f.write(f"{json_to_write},\n")
        except Exception as e:
            print(res)
            logging.debug(e)
        logger.info("Wrote results for source URL: %s", url)
    return res


async def write_file(file: IO, urls: set, **kwargs) -> None:
    """Crawl & write concurrently to 'file' for multiple 'urls'."""
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(
                parse_to_file(file=file, url=url, session=session, **kwargs)
            )
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    import pathlib
    import sys

    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    here = pathlib.Path(__file__).parent

    with open(here.joinpath("data/category_meal_link.csv")) as inputfile:
        category_meal_link = pd.read_csv(inputfile, header=0)

    outpath = here.joinpath("data/recipes_raw.json")
    with open(outpath, "w") as outputfile:
        outputfile.write("[\n") #url,category,recipe\n")

    max_it = len(category_meal_link["link"])

    asyncio.run(write_file(file=outpath, urls=category_meal_link["link"]))

    with open(outpath, "r") as outputfile:
        file_lines = outputfile.readlines()
        len_file_lines = len(file_lines)

    file_lines[len_file_lines-1] = "}\n]"

    with open(outpath, "w") as outputfile:
        outputfile.writelines(file_lines)
