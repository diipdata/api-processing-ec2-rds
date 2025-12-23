# Processamento de API em EC2 e RDS


### RDS

Neste projeto, o RDS/PostregreSQL está em uma subrede pública, para que o acesso externo do RDS ao pgadmin é seja feita de forma facilitada.

Esse processo foi desenhado esecíficamente para esse projeto à carater de estudo/dev. Em modo de produção o acesso ao banco de dados deve ser extremamente restrito, tendo politícas de acesso bem restritas e caso seja necessário fazer o acesso externo, esse deve ser via NAT gateway, serviço que é pago dentro da AWS, porém fornece acesso seguro de aplicações externas aos serviços da aws.

