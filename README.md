# Execução e fluxo de dados

1. monitoramento/models.py: define as entidades Station e Observation, seus campos e relacionamentos.
2. Migrations: criam e atualizam a estrutura das tabelas no banco SQLite.
3. scripts/seed.py: gera dados sintéticos de níveis dos rios e intensidade de chuva, exportando para data/observations.csv.
4. monitoramento/management/commands/import_csv.py: lê o CSV e utiliza o Django ORM para inserir ou atualizar as observações no banco.
5. API REST: disponibiliza os dados persistidos por meio dos endpoints.

## Sequência de comandos a executar
1. python manage.py makemigrations  #Gerar as migrações a partir dos modelos:
2. python manage.py migrate  #Aplicar as migrações no SQLite
3. python scripts/seed.py  #Gerar os dados sintéticos
4. python manage.py import_csv  #Importar os dados para o banco
5. python manage.py runserver  #Iniciar a API REST
