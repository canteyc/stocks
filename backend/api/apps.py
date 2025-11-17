import os
import requests
from django.apps import AppConfig
from dotenv import load_dotenv


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        print("Fetching stock symbols from Finnhub...")
        from . import symbol_cache

        load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
        api_key = os.environ.get("FINNHUB_API_KEY")
        
        if api_key:
            headers = {'X-Finnhub-Token': api_key}
            response = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US', headers=headers)
            symbol_cache.SYMBOLS = response.json()
            # sort symbols alphabetically by 'displaySymbol'
            symbol_cache.SYMBOLS.sort(key=lambda x: x['displaySymbol'])
            print(f"Successfully cached {len(symbol_cache.SYMBOLS)} symbols.")