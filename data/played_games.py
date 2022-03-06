import asyncio
from typing import List

import requests
from pandas import DataFrame, concat, read_html
from data.params import MONTHS, basketball_reference_abbreviations

from utils.uAsync import fetch_api_data
from utils.uDatalake import BlobConnection
from utils.uDatetime import NOW, TODAY, convert_date


def find_abbreviation(team: str) -> str:
    """Function to return team abbreviation"""
    return basketball_reference_abbreviations[team]


def gen_url(row) -> str:
    """Function to find url for stats per game"""
    team = row["AbbrHomeTeam"]
    date = row["DateStr"]
    url = f"https://www.basketball-reference.com/boxscores/{date}0{team}.html"
    return url


def fetch_played_games(months: List[str]) -> DataFrame:
    """Function to retrieve all played NBA games this season"""
    base_url = "https://www.basketball-reference.com/leagues/NBA_2022_games-{}.html"
    urls = [base_url.format(month) for month in months]
    responses = asyncio.run(fetch_api_data(urls))
    games = concat([read_html(r)[0] for r in responses])
    games = games.loc[games["Attend."] > 0]

    games["AbbrHomeTeam"] = games["Home/Neutral"].map(find_abbreviation)
    games["AbbrVisitorTeam"] = games["Visitor/Neutral"].map(find_abbreviation)
    games["DateStr"] = games["Date"].map(convert_date)
    games["Date"] = games["Date"].apply(lambda x: convert_date(x, hyphens=True))
    games["url"] = games.apply(gen_url, axis=1)
    print("Played games fetched...")
    return games


def load_played_games_to_blob(data: DataFrame) -> None:
    """Function to load player games to Azure blob storage"""
    blob_conn = BlobConnection()
    blob_conn.write_dataframe_to_csv(
        data=data, container="gamesplayed", blob_name=f"gamesplayed/{NOW}.csv"
    )
    print("Played games loaded to blob...")


if __name__ == "__main__":
    games = fetch_played_games(MONTHS)
    load_played_games_to_blob(games)
