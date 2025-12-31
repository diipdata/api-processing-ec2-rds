Detalhes Tecnicos do Modulo de Ingestao
O modulo de ingestao e responsavel pelo ciclo de vida dos dados desde a origem ate o destino final no Data Lake e no Data Warehouse.

Fluxo de Execucao
O script principal utiliza a biblioteca schedule para garantir a periodicidade das consultas sem a necessidade de ferramentas externas como Cron.

1. Extracao (API)
A consulta e realizada no endpoint v2 da CoinMarketCap. Os dados sao recebidos em formato JSON e filtrados para extrair apenas a cotacao em BRL (Real).

2. Persistencia no Data Lake (S3)
Apos a coleta, o script gera um arquivo CSV local. Este arquivo e enviado ao Amazon S3 seguindo uma estrutura de particionamento temporal: raw/bitcoin/year=YYYY/month=MM/day=DD/ Este padrao e otimizado para ferramentas de Big Data como o AWS Athena, permitindo a reducao de custos em consultas ao realizar o scan apenas das pastas necessarias.

3. Persistencia no Data Warehouse (RDS)
Os dados sao inseridos em uma instancia de PostgreSQL hospedada no Amazon RDS. A conexao e gerenciada via psycopg2, utilizando um bloco de execucao que garante o commit apenas em caso de sucesso na transacao.