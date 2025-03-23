from pprint import pprint

from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="123", api_url="http://147.93.104.209:3002")

# Scrape a website:
scrape_result = app.scrape_url('https://comp.utm.my/',     params={
        'formats': ['markdown'],
        # 'actions': [
        #     {"type": "wait", "milliseconds": 2000},
        # ]
    })
pprint(scrape_result)