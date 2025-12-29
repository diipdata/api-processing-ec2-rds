# Pipeline de Dados Bitcoin: API para S3 e RDS (PostgreSQL)

Este projeto implementa um pipeline automatizado de ingestão de dados para monitoramento do preço do Bitcoin. O sistema realiza a coleta, normalização, armazenamento em Data Lake (S3) e persistência em banco de dados relacional (RDS).

Todo o processamento é containerizado com **Docker** e orquestrado em uma instância **AWS EC2**, garantindo escalabilidade e isolamento.

---

## Arquitetura do Sistema

O fluxo de dados segue a estrutura abaixo:

1.  **Ingestão**: Script Python consome a API da *CoinMarketCap*.
2.  **Processamento**: Otimização de tipos e formatação de dados.
3.  **Armazenamento Local**: Geração de CSV para auditoria/debug.
4.  **Data Lake (S3)**: Envio do CSV particionado por data (`year/month/day`).
5.  **Data Warehouse (RDS)**: Inserção dos dados em PostgreSQL para consumo analítico.

**Stack Tecnológica:**
* **Linguagem:** Python 3.12
* **Gestão de Dependências:** [uv](https://github.com/astral-sh/uv) (Alta performance)
* **Infraestrutura:** AWS EC2, S3 e RDS (PostgreSQL)
* **Containerização:** Docker

---

## Estrutura do Projeto

```text
.
├── src/
│   └── main.py          # Script principal de ingestão e agendamento
├── data/                # Armazenamento local temporário (CSVs)
├── Dockerfile           # Definição da imagem Docker
├── pyproject.toml       # Configurações do projeto e dependências
├── uv.lock              # Lockfile para reprodutibilidade (uv)
├── .dockerignore        # Otimização do build Docker
└── .env                 # Variáveis sensíveis (não versionado)
```

## Configuração e Instalação

1. Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto com as seguintes chaves:

```
# CoinMarketCap
CMC_API_KEY=sua_chave_aqui

# PostgreSQL (RDS)
DB_HOST=seu-rds-endpoint.amazonaws.com
DB_PORT=5432
DB_NAME=bitcoin_db
DB_USER=postgres
DB_PASS=sua_senha

# AWS Credentials
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
AWS_DEFAULT_REGION=us-east-1
```

2. Execução com Docker
O projeto utiliza o gerenciador uv dentro do container para máxima performance.

**Build da imagem:**
```docker build -t bitcoin-processor .```

**Execução do container:**

```
docker run -d \
  --name processor \
  --env-file .env \
  --restart always \
  bitcoin-processor
```

## Detalhes de Armazenamento

**S3 (Data Lake)**
Os arquivos são organizados em partições para facilitar consultas via Athena ou processos de ETL futuros: raw/bitcoin/year=YYYY/month=MM/day=DD/bitcoin_YYYY-MM-DD_HH-MM-SS.csv

**RDS (PostgreSQL)**
A tabela bitcoin_precos é criada automaticamente com a seguinte estrutura:

```
price: Valor em BRL.

volume_24h: Volume de negociações.

market_cap: Capitalização de mercado.

last_updated: Timestamp da última atualização da API.

inserted_at: Timestamp da inserção no banco.
```


Acesso da ec2-dashboar pelo mesmo key pair já criado. 
Selecionado o mesmo grupo.



## Próximos Passos
[x] Ingestão automática a cada 5 minutos.

[x] Integração com AWS S3 e RDS.

[x] Containerização e Deploy na EC2.

[ ] Desenvolvimento de Dashboard Streamlit para visualização em tempo real.

[ ] Configuração de segurança e acesso público ao dashboard.


Status do Projeto: Pipeline de Ingestão em Produção.