
import csv
from pathlib import Path 
from django.conf import settings 
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction 
from django.utils.dateparse import parse_datetime 
from monitoring.models import Station, Observation # Importa os modelos que representam as tabelas do banco de dados.


class Command(BaseCommand):

    # Descrição exibida quando o usuário consulta a ajuda do comando.
    help = "Importa observações de um arquivo CSV para o banco de dados."

    # Método executado quando o comando é chamado pelo terminal.
    def handle(self, *args, **options):

        # Define o caminho do arquivo CSV a partir da pasta raiz do projeto.
        csv_path = (
            Path(settings.BASE_DIR)
            / "data"
            / "observations.csv"
        )

        # Verifica se o arquivo CSV existe antes de iniciar a importação.
        if not csv_path.exists():
            raise CommandError(
                f"Arquivo CSV não encontrado: {csv_path}"
            )

        # Inicializa o contador de novas observações inseridas.
        imported_count = 0

        try:
            # Abre o CSV em modo de leitura, utilizando UTF-8.
            with csv_path.open(
                mode="r",
                encoding="utf-8",
                newline=""
            ) as file:

                # Organiza cada linha do CSV como um dicionário, utilizando os nomes das colunas como chaves.
                reader = csv.DictReader(file)

                # Define as colunas obrigatórias para a importação.
                required_columns = {
                    "station_id",
                    "metric",
                    "observed_at",
                    "value",
                    "unit",
                    "source",
                }

                # Verifica se todas as colunas necessárias estão presentes.
                if not required_columns.issubset(
                    reader.fieldnames or []
                ):
                    raise CommandError(
                        "O CSV não contém todas as colunas necessárias."
                    )

                # Inicia uma transação no banco de dados. Se ocorrer um erro, as alterações serão revertidas.
                with transaction.atomic():

                    # Percorre todas as linhas do arquivo CSV.
                    for row in reader:

                        # Busca a estação correspondente ao identificador informado na coluna station_id.
                        station = Station.objects.get(
                            pk=row["station_id"]
                        )

                        # Converte a data e hora do CSV para datetime.
                        observed_at = parse_datetime(
                            row["observed_at"]
                        )

                        # Interrompe a importação se a data for inválida.
                        if observed_at is None:
                            raise CommandError(
                                f"Data inválida: {row['observed_at']}"
                            )

                        # Procura uma observação com a mesma estação, métrica e data/hora.
                        # Se encontrar, atualiza os valores. Caso contrário, cria um novo registro.
                        _, created = Observation.objects.update_or_create(
                            station=station,
                            metric=row["metric"],
                            observed_at=observed_at,
                            defaults={
                                # Converte o valor numérico do CSV para float.
                                "value": float(row["value"]),

                                # Armazena a unidade de medida.
                                "unit": row["unit"],

                                # Armazena a origem dos dados.
                                "source": row["source"],
                            },
                        )

                        # Incrementa o contador somente quando uma nova observação é criada.
                        if created:
                            imported_count += 1

        # Captura erros relacionados à estação, aos valores e às colunas esperadas no arquivo.
        except (Station.DoesNotExist, ValueError, KeyError) as error:
            raise CommandError(
                f"Erro durante a importação: {error}"
            ) from error

        # Exibe uma mensagem de sucesso no terminal com a quantidade de novas observações inseridas.
        self.stdout.write(
            self.style.SUCCESS(
                f"Importação concluída! "
                f"{imported_count} novas observações inseridas."
            )
        )
