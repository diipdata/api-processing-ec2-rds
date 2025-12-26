# Processamento de API em EC2 e RDS

Fluxo final da arquitetura

CoinMarketCap API
        ↓
EC2 ETL (Python)
        ↓
   S3 (raw)
        ↓
RDS PostgreSQL
        ↓
EC2 Streamlit (Dashboard)




### RDS

Neste projeto, o RDS/PostregreSQL está em uma subrede pública, para que o acesso externo do RDS/PostregreSQL via pgadmin é seja feita de forma facilitada.

Esse processo foi desenhado esecíficamente para esse projeto à carater de estudo/dev. Em modo de produção o acesso ao banco de dados deve ser extremamente restrito, com politicas de acesso restritivas e caso seja necessário fazer o acesso externo, esse deve ser via NAT gateway, serviço que é pago dentro da AWS, porém fornece acesso seguro de aplicações externas aos serviços da aws.

Outra opção seria fazer o acesso via Bastian Host, mas que nesse projeto traria uma complexidade desnecessária. Caso queira ver um projeto com esse tipo de arquitetura, clique aqui e veja um projeto realizado com essa aquitetura.

### Adicionando s3 como datalake e fonte da verdade.

A utilização de S3 nesse projeto, na prática é utilizado com Data Lake onde teremos o histório bruto da extração da API (raw). Esse S3 se torna a fonte da verdade do projeto, trazendo uma camada barata e escalável para o projeto.

A dúvida comum seria:

> "Se estou utilizando RDS porque salvar no s3 novamente? Não é redundante?"

Aqui alguns pontos importantes sobre o RDS:

1 - RDS não é bom para histórico infinito
2 - RDS é caro para grandes volumes
3 - S3 é barato e infinito

Utilizando o s3, podemos reprocessar dados se necessário, criar novos modelos e até mesmo auditar dados antigos


### Porque adicionar EC2 nesse projeto

A utilização do Ec2 nesse projeto é uma decisão técnica.
A motivação é segregar e definir cada ferramenta com uma respectiva responsabilidade.

Aqui o ec2 permite processamento contínuo 24/7 (loop/scheduler) e cada instância só roda pipelines.

A separação de uma instância para pipeline e outra para streamlit, também fornece outros benefícios técnicos.

O Streamlit consome memória, pode cair e separamos as portas e acessos, fornecendo maior segurança para as aplicações.

#### A separação de responsabilidades fica assim:

EC2	Função
EC2 #1	ETL / processamento
EC2 #2	Aplicação / Dashboard
RDS	Dados
S3	Histórico

### Segurança real para a aplicação

EC2 ETL:

- Sem porta pública
- Só sai para internet

EC2 Streamlit:

- Porta 8501 aberta
- Security Group restrito

RDS:
- Acessível apenas pelas EC2


## Estimativa de custos (AWS) -> Até fetch4.py

Este projeto foi desenhado para ser barato em ambiente de estudo, mas não é totalmente gratuito.
Os valores abaixo são aproximados e variam por região (eu-west-3 – Paris).

Componente	Custo estimado mensal	Observação
S3 (datalake)	US$ 0,10 – 1,00	Dados CSV brutos
RDS PostgreSQL	US$ 15 – 18	Principal responsável pelo custo
EC2 (processamento Python)	US$ 7 – 9	Rodando 24/7
EC2 (dashboard Streamlit)	US$ 7 – 9	Opcional
CloudWatch Logs	US$ 0 – 1	Monitoramento

Total previsto: ~ US$ 32–40 / mês
(aprox. US$ 16–20 por quinzena)

Esses valores serão revisados conforme novos recursos forem adicionados.

# Aprendizados

boto3 - Comunicação com AWS
    - criação RDS
    - Deleção RDS

Mas não é possível subir os dados para o RDS
    - Com o boto3, subimos csv para o S3, mas não diretamente para o RDS

Esse upload de dados para o RDS/postgreSQL é feito pelo psycopg2


diferenças entre datetime.utcnow() e datetime.now(timezone.utc)
Porque é melhor utilizar **datetime.now(timezone.utc)** e o formato **f"bitcoin_{agora.strftime('%Y-%m-%d_%H-%M-%S')}.csv"**


