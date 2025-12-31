FAQ Técnico de Arquitetura
1. Qual a vantagem de separar os Security Groups para cada instância EC2?
A separação segue o Princípio do Menor Privilégio. A instância de Ingestão precisa apenas de acesso de saída para a API e S3, enquanto a instância de Dashboard precisa de acesso de entrada na porta 8501. Ao isolá-las, garantimos que uma eventual vulnerabilidade no servidor web do Dashboard não exponha as credenciais de escrita do Ingestor, e vice-versa.

2. Por que manter o RDS, S3 e EC2 na mesma VPC?
Manter os recursos na mesma Virtual Private Cloud (VPC) permite que a comunicação entre a EC2 e o RDS ocorra através da rede interna da AWS (utilizando IPs privados). Isso resulta em baixa latência, redução de custos de transferência de dados e, principalmente, segurança, pois o tráfego do banco de dados nunca transita pela internet pública.

3. Por que utilizar Dockerfile e Docker Compose simultaneamente?
O Dockerfile define a "receita" da imagem (instalação do Python, uv, e dependências), garantindo imutabilidade. O Docker Compose atua como o orquestrador, definindo como esses containers devem rodar (mapeamento de portas, volumes para logs e carregamento de variáveis de ambiente do arquivo .env). Essa combinação facilita o deploy padronizado em diferentes ambientes.

4. Por que utilizar o gerenciador de pacotes 'uv' em vez do pip tradicional?
O uv foi escolhido por sua performance superior e pela capacidade de gerar um uv.lock extremamente rigoroso. Em um ambiente de produção (EC2), isso garante que a instalação das dependências seja determinística, evitando erros causados por sub-dependências que poderiam variar em uma instalação comum via pip.

5. Por que a arquitetura foi dividida em dois nós (Ingestor e Dashboard)?
Essa divisão permite o escalonamento independente. Se o tráfego de usuários no Dashboard aumentar, podemos escalar apenas a instância de visualização sem afetar a coleta de dados. Além disso, evita a disputa de recursos (CPU/RAM) entre o processo de escrita pesada no banco e a renderização de gráficos para o usuário final.