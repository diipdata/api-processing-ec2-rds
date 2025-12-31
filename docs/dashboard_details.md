Detalhes Tecnicos do Modulo de Dashboard
O modulo de visualizacao foi desenvolvido para fornecer insights em tempo real sobre os dados armazenados no banco de dados relacional.

Conectividade
O Dashboard nao possui conexao direta com a API da CoinMarketCap nem com o S3. Ele atua exclusivamente como um consumidor do Amazon RDS. Isso garante que a visualizacao reflita exatamente o que foi persistido no banco de dados oficial do projeto.

Interface Streamlit
A interface utiliza os seguintes componentes:

Metricas: Exibicao do ultimo preco coletado comparado ao registro anterior para calculo de variacao percentual.

Plotly Express: Utilizado para renderizar graficos de linha interativos que permitem zoom e inspecao de pontos especificos de tempo.

Dataframes: Exibicao dos ultimos 100 registros para auditoria rapida dos dados processados.

Performance
Para evitar sobrecarga no banco de dados e na rede, o dashboard utiliza um sistema de cache simples e permite a atualizacao manual dos dados atraves de um botao dedicado, minimizando requisições desnecessarias ao RDS.


2. **Deploy Distribuído via Docker Compose**

- O projeto utiliza o Docker Compose para gerenciar os serviços de forma isolada em cada instância

  **Na Instância Ingestor (EC2 Ingestor)** - Responsável pela coleta e carga de dados.

    - **Execução do container:**

      ```
      docker compose up -d --build ingestor
      ```

      

  **Na Instância Dashboard (EC2 Dashboard)** - Responsável pela interface do usuário.
    - **Execução do container:**

      ```
      docker compose up -d --build dashboard
      ```

      