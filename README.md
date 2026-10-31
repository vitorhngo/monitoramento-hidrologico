## Fluxo de execução do arquivo 'seed.py'

A geração dos dados simulados é iniciada pelo arquivo `seed.py`, executado pelo comando:

```bash
python seed.py
```

O processo segue as seguintes etapas:

1. **Inicialização:** o `seed.py` carrega as configurações do Django por meio de `setup/settings.py`.
2. **Importação:** carrega os models `Station` e `Observation`, definidos em `monitoramento/models.py`.
3. **Geração:** executa a função `seed()`, responsável por gerar as estações e suas observações simuladas.
4. **Persistência:** utiliza o Django ORM para inserir ou atualizar os registros no banco de dados.
5. **Armazenamento:** o Django gerencia a conexão configurada em `settings.py` e persiste os dados no SQLite.

**Arquivos envolvidos:**

| Arquivo | Responsabilidade |
|---|---|
| `seed.py` | Geração e inserção dos dados simulados. |
| `setup/settings.py` | Configurações do projeto e do banco de dados. |
| `monitoramento/models.py` | Definição das entidades e seus campos. |
| `monitoramento/migrations/` | Controle das alterações na estrutura das tabelas. |

**Execução inicial:** antes de gerar os dados, crie as tabelas com:

```bash
python manage.py makemigrations
python manage.py migrate
python seed.py
```