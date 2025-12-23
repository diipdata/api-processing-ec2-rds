#IMPORTS
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
import os
import json

#LOAD ENV VARIABLES
load_dotenv()

url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'

# PARAMETERS AND HEADERS
parameters = {
    'symbol': 'BTC', # Identificando moeadas pelo simbolo
    'convert': 'BRL'         # Convertendo os valores para Dolar Americano
}

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': os.getenv('CMC_API_KEY'), # Obtendo a chave da API do arquivo .env
}

# ABRINDO SESSAO
session = Session()
session.headers.update(headers)

response = session.get(url=url, params=parameters)

print(response)