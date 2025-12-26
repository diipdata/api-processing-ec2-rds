#IMPORTS
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
import os
import json
from pprint import pprint

#LOAD ENV VARIABLES
load_dotenv()

url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

# PARAMETERS AND HEADERS
parameters = {
    "symbol": "BTC", # Identificando moeadas pelo simbolo
    "convert": "BRL"         # Convertendo os valores para Dolar Americano
}

headers = {
  "Accepts": "application/json",
  "X-CMC_PRO_API_KEY": os.getenv("CMC_API_KEY"), # Obtendo a chave da API do arquivo .env
}

# ABRINDO SESSAO
session = Session()
session.headers.update(headers)

# Função auxiliar para formatar números grandes
def format_large_number(value):
            if value is None:
                return "N/A"

            abs_value = abs(value)

            if abs_value >= 1_000_000_000_000:
                return f"{value / 1_000_000_000_000:.2f} T" # Trilhão
            elif abs_value >= 1_000_000_000:
                return f"{value / 1_000_000_000:.2f} B" # Bilhão
            elif abs_value >= 1_000_000:
                return f"{value / 1_000_000:.2f} M" # Milhão
            elif abs_value >= 1_000:
                return f"{value / 1_000:.2f} K" # Mil
            else:
                return f"{value:.2f}"

# função para consultar a cotação do Bitcoin
def consultar_cotação_bitcoin():
    try:
        response = session.get(url=url, params=parameters)
        data = json.loads(response.text)
        
        # MANIPULANDO DADOS (dict)
        if 'data' in data and 'BTC' in data['data']:
          bitcoin_data = data["data"]["BTC"][0]
          brl_quote = bitcoin_data["quote"]["BRL"]

          #pprint(brl_quote)
          # EXIBINDO DADOS FORMATADOS
          pprint(f"Última cotação do Bitcoin: R$ {format_large_number(brl_quote['price'])} BRL")
          pprint(f"Volume 24h: R$ {format_large_number(brl_quote['volume_24h'])}")
          pprint(f"Market Cap: R$ {format_large_number(brl_quote['market_cap'])}")
          pprint(f"Última atualização: ${brl_quote['last_updated']}")
        else:
          print("Erro ao tentar obter os dados do Bitcoin:", data['status'].get('error_message', 'Unknown error'))

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)  


consultar_cotação_bitcoin()
