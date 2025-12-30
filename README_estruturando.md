# Pipeline de Dados Bitcoin: API para S3 e RDS (PostgreSQL) com Dashboard Distribuído

Este projeto implementa um pipeline automatizado de ingestão de dados para monitoramento do preço do Bitcoin. A solução abrange desde a ingestão de APIs de terceiros passando por normalização, armazenamento em Data Lake (S3), persistência em banco de dados relacional (RDS) até a visualização em tempo real no Streamlit, utilizando uma arquitetura distribuída na AWS.

Todo o processamento é containerizado com **Docker**, gerenciado pelo **uv** e orquestrado via **Docker Compose** em instâncias **AWS EC2** distintas, garantindo escalabilidade e isolamento.

## Arquitetura do Sistema

O projeto foi desenhado para separar as responsabilidades de escrita (Ingestão) e leitura (Dashboard), garantindo maior resiliência.

#### 1. **Ingestão (EC2 A)**: Script Python consome a API da CoinMarketCap a cada 5 minutos.

#### **Armazenamento Híbrido**:

  - **Armazenamento Local**: Geração de CSV para auditoria/debug.

  - **Data Lake (S3)**: Dados brutos salvos em CSV particionados por data `year/month/day` para futuras análises de Big Data (AWS Athena/PowerBI).

  - **Data Warehouse (RDS)**: Dados estruturados em PostgreSQL para consultas de baixa latência.

4. **Data Lake (S3)**: Envio do CSV particionado por data (`year/month/day`).

5. **Visualização (EC2 B)**: Dashboard Streamlit que consome o RDS e apresenta KPIs e gráficos históricos.

#### **Stack Tecnológica:**
* **Linguagem:** Python 3.12
* **Gestão de Dependências:** [uv](https://github.com/astral-sh/uv) (Alta performance)
* **Banco de Dados**: AWS RDS (PostgreSQL)
* **Object Storage**: AWS S3
* **Compute**: AWS EC2 (Ubuntu 24.04 LTS)
* **Containerização**: Docker & Docker Compose
* **Visualização**: Streamlit & Plotly


## Estrutura do Projeto

```text
.
├── src/
│   ├── main.py          # Script de ingestão 
│   └── dashboard.py     # Script do Dashboard 
├── data/                # Cache local de CSVs
├── Dockerfile           # Imagem base utilizando uv
├── docker-compose.yml   # Orquestração dos serviços
├── pyproject.toml       # Dependências do projeto
├── uv.lock              # Lockfile de alta precisão
└── .env                 # Variáveis sensíveis (não versionado)
```

## Configuração e Deploy

#### 1. **Variáveis de Ambiente (.env)**
  - O arquivo .env deve ser configurado em ambas as instâncias EC2:

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

#### 2. **Deploy Distribuído via Docker Compose**

- O projeto utiliza o Docker Compose para gerenciar os serviços de forma isolada em cada instância

  **Na Instância Ingestor (EC2-A)** - Responsável pela coleta e carga de dados.

    - **Execução do container:**

      ```
      docker compose up -d --build ingestor
      ```

      - [Clique aqui para ver a explicação técnica do Ingestor](./docs/ingestor_details.md)

  **Na Instância Dashboard (EC2-B)** - Responsável pela interface do usuário.
    - **Execução do container:**

      ```
      docker compose up -d --build dashboard
      ```

      - [Clique aqui para ver a explicação técnica do Dashboard](docs/dashboard.py)


## Visualização e Dados
**Dashboard em Tempo Real**

O dashboard pode ser acessado via navegador na porta 8501. Ele oferece:

- **KPIs**: Preço atual, Volume 24h e Market Cap.

- **Gráfico de Tendência**: Histórico de variação de preço.

- **Data Analysis**: Tabela detalhada dos últimos registros inseridos.

**Acesse aqui**: http://13.38.82.54:8501/

## Modelagem do Banco (RDS)
- A tabela bitcoin_precos é estruturada para séries temporais:

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| price | NUMERIC(18,2) | Preço em BRL |
| volume_24h | NUMERIC(24,2) | Volume total negociado |
| last_updated | TIMESTAMP | Horário oficial da cotação |
| inserted_at | TIMESTAMP | Registro de entrada no banco |


## Detalhes de Armazenamento

**S3 (Data Lake)**
- Os arquivos são organizados em partições para facilitar consultas via Athena ou processos de ETL futuros: 

```raw/bitcoin/year=YYYY/month=MM/day=DD/bitcoin_YYYY-MM-DD_HH-MM-SS.csv```

## Segurança e Boas Práticas
- **Security Groups**: A porta 5432 do RDS está aberta apenas para os IPs privados das instâncias EC2.

- **Acesso Externo**: A porta 8501 do dashboard está protegida via regras de entrada no SG da AWS.

- **Identidade**: Ambas as instâncias utilizam o mesmo par de chaves SSH (.pem) para gerenciamento simplificado.



## Status do Projeto
[x] Ingestão automática (API -> S3/RDS).

[x] Arquitetura de containers com Docker.

[x] Deploy em múltiplas instâncias EC2.

[x] Dashboard Streamlit funcional.

[ ] Implementação de alertas de preço via Telegram.

[ ] Automação de Infraestrutura via Terraform (IaC).

Status: Projeto em Produção e Funcional.