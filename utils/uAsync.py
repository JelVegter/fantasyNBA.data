import aiohttp
import asyncio


async def fetch(session, url: str):
    """Helper function to retrieve data async"""
    async with session.get(url, ssl=False) as response:
        data = await response.read()
        return data


async def fetch_api_data(urls: list) -> tuple:
    """Main function to retrieve data async"""
    print("Fetching data...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(session, url))
        responses = await asyncio.gather(*tasks, return_exceptions=False)
    return responses
