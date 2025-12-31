# IMPORTS
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
import os
import json
from pprint import pprint
import schedule
import time
import csv
import psycopg2 #psycopg2-binary
from psycopg2 import sql
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime, timezone

# ==============================================
# CONFIGURAÇÕES
# ==============================================

load_dotenv()

DATA_DIR = 'data'
CSV_FILE = os.path.join(DATA_DIR, 'bitcoin.csv')

CMC_API_KEY = os.getenv("CMC_API_KEY")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

print("=== DEBUG VARIÁVEIS DE AMBIENTE ===")
print(f"DB_HOST: {DB_HOST}")
print(f"DB_PORT: {DB_PORT}")
print(f"DB_NAME: {DB_NAME}")
print(f"DB_USER: {DB_USER}")
print(f"DB_PASS: {DB_PASS[:3]}... (ocultado)")
print("===================================")

API_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
PARAMS = {"symbol": "BTC", "convert": "BRL"}
HEADERS = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC_API_KEY}

S3_BUCKET = "datalake-api-bitcoin-prod"

# ==============================================
# FUNÇÕES AUXILIARES
# ==============================================

def format_large_number(value):
    if value is None:
        return "N/A"
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f}T"
    elif abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif abs_value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return f"{value:.2f}"

def parse_timestamp(ts_str):
    """Converte string ISO da API para datetime"""
    try:
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except Exception:
        return None

# ==============================================
# TEMP EM CSV E UPLOAD PARA S3
# ==============================================

def salvar_e_upload_csv_temporario(brl_quote):
    agora = datetime.now(timezone.utc)
    temp_csv = f"/tmp/bitcoin_{agora.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    
    with open(temp_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['price', 'volume_24h', 'market_cap', 'last_updated'])
        writer.writerow([
            brl_quote['price'],
            brl_quote['volume_24h'],
            brl_quote['market_cap'],
            brl_quote['last_updated']
        ])
    
    try:
        s3 = boto3.client("s3")
        key = (
            f"raw/bitcoin/"
            f"year={agora.year}/"
            f"month={agora.month:02}/"
            f"day={agora.day:02}/"
            f"bitcoin_{agora.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        )
        s3.upload_file(Filename=temp_csv, Bucket=S3_BUCKET, Key=key)
        print("CSV temporário enviado para o S3 com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar para o S3: {e}")
    finally:
        if os.path.exists(temp_csv):
            os.remove(temp_csv)  # limpa o temporário

# ==============================================
# BANCO DE DADOS
# ==============================================

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def criar_tabela():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Cria a tabela se não existir
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bitcoin_precos (
                        id SERIAL PRIMARY KEY,
                        price NUMERIC(18,2),
                        volume_24h NUMERIC(24,2),
                        market_cap NUMERIC(24,2),
                        last_updated TIMESTAMP WITH TIME ZONE,
                        inserted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Remove duplicatas mantendo o registro mais antigo (menor id)
                cursor.execute("""
                    DELETE FROM bitcoin_precos a USING (
                        SELECT MIN(id) as keep_id, last_updated
                        FROM bitcoin_precos 
                        GROUP BY last_updated
                        HAVING COUNT(*) > 1
                    ) b
                    WHERE a.last_updated = b.last_updated 
                    AND a.id != b.keep_id;
                """)

                # Agora tenta criar a constraint única
                cursor.execute("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'unique_last_updated'
                              AND conrelid = 'bitcoin_precos'::regclass
                        ) THEN
                            ALTER TABLE bitcoin_precos 
                            ADD CONSTRAINT unique_last_updated UNIQUE (last_updated);
                        END IF;
                    END $$;
                """)

            conn.commit()
        print("Tabela configurada, duplicatas removidas e constraint única criada com sucesso!")
    except Exception as e:
        print(f"Erro ao configurar tabela: {e}")

def salvar_no_banco(brl_quote):
    try:
        last_updated_dt = parse_timestamp(brl_quote['last_updated'])
        
        if last_updated_dt is None:
            print("Erro: timestamp inválido da API, pulando inserção.")
            return

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO bitcoin_precos 
                    (price, volume_24h, market_cap, last_updated)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (last_updated) DO NOTHING
                """, (
                    brl_quote['price'],
                    brl_quote['volume_24h'],
                    brl_quote['market_cap'],
                    last_updated_dt
                ))
            conn.commit()
        
        # Verifica se inseriu algo novo
        if cursor.rowcount > 0:
            print("Novo dado inserido com sucesso no banco.")
        else:
            print("Dado duplicado (mesmo last_updated) — ignorado (idempotência).")

    except Exception as e:
        print(f"Erro ao inserir no banco: {e}")

# ==============================================
# CONSULTA PRINCIPAL
# ==============================================

def consultar_e_salvar():
    session = Session()
    session.headers.update(HEADERS)

    try:
        response = session.get(API_URL, params=PARAMS, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and 'BTC' in data['data']:
            btc = data['data']['BTC'][0]
            brl = btc['quote']['BRL']

            # Exibe formatado
            print(f"\n[{brl['last_updated']}]")
            print(f"Preço:       R$ {format_large_number(brl['price'])}")
            print(f"Volume 24h:  R$ {format_large_number(brl['volume_24h'])}")
            print(f"Market Cap:  R$ {format_large_number(brl['market_cap'])}")

            # Salva nos dois destinos
            salvar_e_upload_csv_temporario(brl)
            salvar_no_banco(brl)

        else:
            error_msg = data.get('status', {}).get('error_message', 'Erro desconhecido')
            print(f"Erro na API: {error_msg}")

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(f"Erro de rede: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        session.close()

# ==============================================
# INICIALIZAÇÃO E AGENDAMENTO
# ==============================================

if __name__ == "__main__":
    print("Inicializando script de monitoramento do Bitcoin...")
    
    criar_tabela()
    
    # Sugestão: 5 minutos (300 segundos) para não estourar limite da API
    schedule.every(5).minutes.do(consultar_e_salvar)
    
    print("Agendamento configurado: consulta a cada 5 minutos")
    
    # Primeira execução imediata
    consultar_e_salvar()
    
    while True:
        schedule.run_pending()
        time.sleep(1)