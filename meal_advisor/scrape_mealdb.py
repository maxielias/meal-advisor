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
import ast
from dateutil.parser import parse


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True


async def fetch_url(url: str, session: ClientSession, **kwargs) -> str:
    """GET request wrapper to fetch page HTML.
    kwargs are passed to 'session.request()'.
    """
    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    logger.info("Got session response [%s] for URL: %s", resp.status, url)
    html = await resp.json()
    # await asyncio.sleep(1)

    return html


async def parse(url: str, session: ClientSession, **kwargs) -> set:
    """Find HREFs in the HTML of 'url'."""
    data = dict()

    try:
        resp = await fetch_url(url=url, session=session, **kwargs)
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
            data = resp["meals"]
            return data

        except Exception as e:
            logger.debug(e)
            return data


async def parse_to_file(file: IO, url: str, **kwargs) -> None:
    """Write the found HREFs from 'url' to 'file'."""
    res = await parse(url=url, **kwargs)
    if not res:
        return None
    async with aiofiles.open(file, "a", encoding="utf-8") as f:
        try:
            for r in res:
                if r["idMeal"]:
                    # logging.debug(r["idMeal"])
                    json_to_append = json.dumps(r, indent=4)
                    await f.write(f"{json_to_append},\n")
        except Exception as e:
            logging.debug(r)
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
    from string import ascii_lowercase

    url_mealdb = "https://www.themealdb.com/api/json/v1/1/search.php?f="
    urls = set()
    for c in ascii_lowercase:
        url_mealdb_to_append = f"{url_mealdb}{c}"
        urls.add(url_mealdb_to_append)
    
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    here = pathlib.Path(__file__).parent

    outpath = here.joinpath("data/recipes_raw_mealdb.json")
    with open(outpath, "w") as outputfile:
        outputfile.write("[\n") #url,category,recipe\n")

    asyncio.run(write_file(file=outpath, urls=list(urls)))

    with open(outpath, "r", encoding="utf-8") as outputfile:
        file_lines = outputfile.readlines()
        len_file_lines = len(file_lines)

    file_lines[len_file_lines-1] = "}\n]"

    with open(outpath, "w", encoding="utf-8") as outputfile:
        outputfile.writelines(file_lines)
