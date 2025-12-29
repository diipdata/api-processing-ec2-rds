import streamlit as st
from streamlit_plotly_events import plotly_events
import plotly.express as px
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Configurações de página
st.set_page_config(page_title="Bitcoin Monitor", page_icon="⚡", layout="wide")

# Carregar variáveis
load_dotenv()

def get_data():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        query = "SELECT * FROM bitcoin_precos ORDER BY last_updated DESC LIMIT 100"

        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return pd.DataFrame()
    
    # Interface Streamlit
st.title("₿ Bitcoin Real-Time Monitor")
st.subheader("Dados extraídos do pipeline API → S3 → RDS")

df = get_data()

if not df.empty:
    # --- KPIs ---
    ultimo_preco = df['price'].iloc[0]
    preco_anterior = df['price'].iloc[1] if len(df) > 1 else ultimo_preco
    variacao = ((ultimo_preco - preco_anterior) / preco_anterior) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Preço Atual (BRL)", f"R$ {ultimo_preco:,.2f}", f"{variacao:.2f}%")
    col2.metric("Volume 24h", f"R$ {df['volume_24h'].iloc[0]:,.0f}")
    col3.metric("Market Cap", f"R$ {df['market_cap'].iloc[0]:,.0f}")

# --- GRÁFICO ---
    st.markdown("### Histórico de Preço (Últimas Leituras)")
    fig = px.line(df, x='last_updated', y='price', labels={'price': 'Preço (R$)', 'last_updated': 'Tempo'})
    st.plotly_chart(fig, width="stretch")

# --- TABELA ---
    st.markdown("### Dados Recentes")
    st.dataframe(df, width="stretch")

else:
    st.warning("Aguardando dados serem carregados do banco...")

# Botão de atualização manual
if st.button('Atualizar Dados'):
    st.rerun()