# Execução e fluxo de dados

1. ./monitoring: app django que organiza a estrutura e separa as responsabilidades das funcionalidades.
2. monitoring/models.py: define as entidades Station e Observation, seus campos e relacionamentos.
3. scripts/seed.py: gera dados sintéticos de níveis dos rios e intensidade de chuva, exportando para data/observations.csv.
4. monitoramento/management/commands/import_csv.py: lê o CSV e utiliza o Django ORM para inserir ou atualizar as observações no banco.

## Ambiente
Garantir que o python da venv esteja selecionado: 
1. Ctrl + Shift + P 
2. Digitar: Python:Select Interpreter
3. Selecionar: venv(3.14.6) .\venv\Scripts\python.exe

## Sequência de comandos a executar
1. python manage.py makemigrations  #Gerar as migrações a partir dos modelos:
2. python manage.py migrate  #Aplicar as migrações no SQLite
3. python scripts/seed.py  #Gerar os dados sintéticos
4. python manage.py import_csv  #Importar os dados para o banco
5. python manage.py runserver  #Iniciar a API REST
