import pandas as pd
import asyncio
import aiohttp
from datetime import datetime, timedelta

# Set your API key
api_key = '_iKZHMntetVbmPXjkf3aSyKuN1FIpUpn'

# Get yesterday's date
yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

# Load the CSV of stock symbols into a DataFrame
df = pd.read_csv('qualified_stock_symbols.csv')

async def fetch_price(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, row in df.iterrows():
            url = f'https://api.polygon.io/v1/open-close/{row[0]}/{yesterday}?unadjusted=true&apiKey={api_key}'
            tasks.append(fetch_price(session, url))

        responses = await asyncio.gather(*tasks)

        for response, ticker in zip(responses, df.itertuples(index=False)):
            if response.get('status') == 'OK':
                print(f"Stock: {ticker[0]}, Yesterday's Close Price: {response['close']}")

# Running the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
