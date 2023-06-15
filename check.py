import requests
import json

def get_volume_from_agg(ticker, date):
    api_key = "_iKZHMntetVbmPXjkf3aSyKuN1FIpUpn"
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date}/{date}?apiKey={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)

    # Ensure the 'results' key is in the data and it has at least one item
    if 'results' in data and len(data['results']) > 0:
        # 'v' corresponds to volume in the 'agg' endpoint response
        volume = data['results'][0]['v']
        return volume
    else:
        return None

# Example usage:
ticker = "AAPL"
date = "2023-06-15"
print(get_volume_from_agg(ticker, date))
