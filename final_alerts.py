import pandas as pd
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
import pytz

# Set your keys
PUSHOVER_API_TOKEN = 'ahh57yeodyhx13vr8mi13xvct51u4u'
PUSHOVER_USER_KEY = 'udnz28vppx6otfciwqu3qj2duaaoz6'
POLYGON_API_KEY = '_iKZHMntetVbmPXjkf3aSyKuN1FIpUpn'

# Set your timezone
local_tz = pytz.timezone('Europe/Kiev')  # replace with your timezone

# Load the CSV of stock symbols into a DataFrame
df = pd.read_csv('qualified_stock_symbols.csv')

# Keep track of stocks that have already sent a notification
notified_stocks = {}

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    while True:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for index, row in df.iterrows():
                # Skip this stock if it has already triggered a notification and it's not yet 3 PM
                now = datetime.now(local_tz)
                if row[0] in notified_stocks and now.hour < 15:
                    continue

                # Get yesterday's date for each stock
                yesterday = (now - timedelta(1)).strftime('%Y-%m-%d')

                tasks.append(fetch(session, f'https://api.polygon.io/v1/open-close/{row[0]}/{yesterday}?unadjusted=true&apiKey={POLYGON_API_KEY}'))
                tasks.append(fetch(session, f'https://api.polygon.io/v2/last/trade/{row[0]}?apiKey={POLYGON_API_KEY}'))

            responses = await asyncio.gather(*tasks)

        for i in range(0, len(responses), 2):
            closing_price_data, current_price_data = responses[i], responses[i+1]
            ticker = df.iloc[i//2][0]
            if closing_price_data.get('status') == 'OK' and current_price_data.get('status') == 'OK':
                closing_price = closing_price_data['close']
                current_price = current_price_data['results']['p']
                if current_price > 1.2 * closing_price:
                    r = requests.post("https://api.pushover.net/1/messages.json", data = {
                        "token": PUSHOVER_API_TOKEN,
                        "user": PUSHOVER_USER_KEY,
                        "message": f"Stock: {ticker} had a price change of more than 20%. Yesterday's close: {closing_price}, Current price: {current_price}"
                    })
                    notified_stocks[ticker] = now
                    print(f"Notification sent for: {ticker}")
        # Sleep for a bit to avoid hitting API rate limits
        await asyncio.sleep(60)

# Running the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
