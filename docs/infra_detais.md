Detalhes da Infraestrutura e Seguranca
A infraestrutura foi desenhada seguindo principios de segregacao de funcoes em ambiente de nuvem.

Seguranca de Rede (Security Groups)
A seguranca e aplicada em camadas:

Instancia Ingestor: Permite apenas saida (Outbound) para API e AWS Services. Entrada (Inbound) restrita a porta 22 (SSH) para administracao.

Instancia Dashboard: Permite entrada na porta 8501 (Streamlit) e porta 22.

Instancia RDS: Configuracao restrita. A regra de entrada permite conexao na porta 5432 apenas se a origem for o ID do Security Group das instancias EC2, impedindo qualquer acesso externo direto ao banco de dados.

Gerenciamento de Dependencias com uv
O uso do uv no Dockerfile permite builds extremamente rapidos e garante que as versoes das bibliotecas sejam identicas em todos os nos do cluster, utilizando o arquivo uv.lock.



mermaid: 

graph TD
    A[CoinMarketCap API] -->|a cada 5 min| B(EC2 Ingestor<br/>main.py)
    B --> C[S3 Bucket<br/>raw/bitcoin/year/month/day/]
    B --> D[RDS PostgreSQL<br/>tabela bitcoin_precos]
    D --> E(EC2 Dashboard<br/>Streamlit + Plotly)
