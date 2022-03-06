import asyncio
from typing import List

from pandas import DataFrame, concat, read_html, to_numeric

from data.params import MONTHS
from data.played_games import fetch_played_games
from utils.uAsync import fetch_api_data
from utils.uDatalake import BlobConnection
from utils.uDatetime import NOW, TODAY, THREE_DAYS_AGO


def parse_html_tables(html: str, date, home_team_ab: str, away_team_ab: str) -> DataFrame:
    """Function to read Basketball-Reference html tables into a Dataframe"""
    away_team = read_html(html)[0]
    away_team["Team"] = away_team_ab
    away_team["Opponent"] = home_team_ab
    away_team["Home/Away"] = "away"
    minutes_played = away_team[("Basic Box Score Stats", "MP")].iloc[-1]
    minutes_played = int(minutes_played)
    nr_overtimes = (minutes_played - 240) / 25
    table_html_index = int(8 + nr_overtimes)

    home_team = read_html(html)[table_html_index]
    home_team["Team"] = home_team_ab
    home_team["Opponent"] = away_team_ab
    home_team["Home/Away"] = "home"
    stats = concat([away_team, home_team])
    stats["GameDay"] = date
    return stats


def fetch_player_stats(played_games: DataFrame, incremental: bool = False) -> DataFrame:
    """Function to fetch all player stats for games played"""

    if incremental:
        played_games = played_games.loc[played_games["DateStr"] > THREE_DAYS_AGO]

    urls = played_games["url"].to_list()
    dates = played_games["Date"].to_list()
    home_teams = played_games["AbbrHomeTeam"].to_list()
    away_teams = played_games["AbbrVisitorTeam"].to_list()

    print("Getting all stats...")
    responses = asyncio.run(fetch_api_data(urls))
    reponses_and_dates = zip(dates, responses, home_teams, away_teams)
    tables = []
    counter = 0
    for date, response, home_team, away_team in reponses_and_dates:
        tables.append(parse_html_tables(response, date, home_team, away_team))
        counter += 1
        if counter % 10 == 0:
            print(f"Parsed {counter} of out {len(responses)} responses")

    all_stats = concat(tables)
    all_stats.reset_index(inplace=True, drop=True)
    print(all_stats)
    return all_stats


def clean_stats_table(player_stats: DataFrame) -> DataFrame:
    cols = [
        "Player",
        "MP",
        "FGM",
        "FGA",
        "FG%",
        "3PTM",
        "3PA",
        "3P%",
        "FTM",
        "FTA",
        "FT%",
        "ORB",
        "DRB",
        "REB",
        "AST",
        "STL",
        "BLK",
        "TO",
        "PF",
        "PTS",
        "+/-",
        "Team",
        "Opponent",
        "Home/Away",
        "GameDay",
    ]
    player_stats.columns = cols

    player_stats = player_stats.loc[
        (player_stats["Player"] != "Starters")
        & (player_stats["Player"] != "Reserves")
        & (player_stats["Player"] != "Team Totals")
    ]

    numeric_cols = [
        "FGM",
        "FGA",
        "FG%",
        "PTS",
        "+/-",
        "3PTM",
        "3PA",
        "3P%",
        "FTM",
        "FTA",
        "FT%",
        "ORB",
        "DRB",
        "REB",
        "AST",
        "STL",
        "BLK",
        "TO",
        "PF",
    ]
    player_stats[numeric_cols] = player_stats[numeric_cols].apply(to_numeric, errors="coerce")
    return player_stats


def load_player_stats_to_blob(data: DataFrame) -> None:
    """Function to load player stats to Azure blob storage"""
    blob_conn = BlobConnection()
    blob_conn.write_dataframe_to_csv(
        data=data, header=False, container="playerstats", blob_name=f"playerstats/{NOW}.csv"
    )
    print("Player stats loaded to blob...")


if __name__ == "__main__":
    played_games = fetch_played_games(MONTHS)
    player_stats = fetch_player_stats(played_games, incremental=False)
    prepped_player_stats = clean_stats_table(player_stats)
    load_player_stats_to_blob(prepped_player_stats)

