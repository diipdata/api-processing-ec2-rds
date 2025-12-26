# etapas de criação desse projeto

### FASE 1 — Mantém CSV + S3 (transição)

API
  ├── salva CSV local
  ├── envia para S3
  └── insere no RDS

Objetivo:

✔ validar S3
✔ testar permissões IAM
✔ garantir que os arquivos chegam
✔ conferir formatos
✔ checar custos
✔ revisar logs

### FASE 2 — Tornar S3 a fonte oficial

API → S3 → RDS

❌ você para de gravar CSV local
✔ mantém leitura se precisar recuperar histórico
✔ foca só no pipeline cloud

#### Aqui você:

comenta / remove bloco do CSV

limpa arquivos antigos se quiser

documenta mudança

### FASE 3 — Movemos tudo para EC2

EC2 → S3 → RDS

Na prática:

o script roda 24/7

EC2 escreve direto no S3

EC2 grava no RDS

Seu computador vira só:

✔ monitor
✔ ambiente de desenvolvimento
✔ testes locais