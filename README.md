## Execução e fluxo de dados

1. monitoramento/models.py: define as entidades Station e Observation, seus campos e relacionamentos.
2. Migrations: criam e atualizam a estrutura das tabelas no banco SQLite.
3. scripts/seed.py: gera dados sintéticos de níveis dos rios e intensidade de chuva, exportando para data/observations.csv.
4. monitoramento/management/commands/import_csv.py: lê o CSV e utiliza o Django ORM para inserir ou atualizar as observações no banco.
5. API REST: disponibiliza os dados persistidos por meio dos endpoints.

# 1. Gerar as migrações a partir dos modelos
python manage.py makemigrations

# 2. Aplicar as migrações no SQLite
python manage.py migrate

# 3. Gerar os dados sintéticos
python scripts/seed.py

# 4. Importar os dados para o banco
python manage.py import_csv

# 5. Iniciar a API REST
python manage.py runserver