import asyncio
from typing import List

import aiohttp
from pandas import DataFrame, concat, read_html

from params import MONTHS


async def fetch(session, url: str):
    """Function to retrieve data async"""
    async with session.get(url, ssl=False) as response:
        data = await response.read()
        return data


async def fetch_api_data(urls: list) -> tuple:
    """ """
    print("Fetching api data...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(session, url))
        responses = await asyncio.gather(*tasks, return_exceptions=False)
    return responses


def fetch_played_games(months: List[str]) -> DataFrame:
    """Function to retrieve all played NBA games this season"""
    base_url = "https://www.basketball-reference.com/leagues/NBA_2022_games-{}.html"
    urls = [base_url.format(month) for month in months]
    responses = asyncio.run(fetch_api_data(urls))
    games = concat([read_html(r)[0] for r in responses])


    # games = games.loc[games["Attend."] > 0]
    # games["AbbrHomeTeam"] = games["Home/Neutral"].map(find_abbreviation)
    # games["AbbrVisitorTeam"] = games["Visitor/Neutral"].map(find_abbreviation)
    # games["DateStr"] = games["Date"].map(convert_date)
    # games["url"] = games.apply(gen_url, axis=1)
    print(games)
    return games


if __name__=="__main__":
    fetch_played_games(MONTHS)