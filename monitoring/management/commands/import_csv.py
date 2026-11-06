import csv
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from monitoring.models import Observation, Station # Modelos que representam as tabelas do banco de dados.


# Colunas obrigatórias de cada CSV.
STATION_COLUMNS = {"id", "name", "river", "municipality"}
OBSERVATION_COLUMNS = {
    "station_id",
    "metric",
    "observed_at",
    "value",
    "unit",
    "source",
}


class Command(BaseCommand):

    # Método executado quando o comando é chamado pelo terminal.
    def handle(self, *args, **options):

        # Define os caminhos dos CSVs a partir da pasta raiz do projeto.
        data_dir = Path(settings.BASE_DIR) / "data"
        stations_path = data_dir / "stations.csv"
        observations_path = data_dir / "observations.csv"

        # Verifica se os arquivos existem antes de iniciar a importação.
        for path in (stations_path, observations_path):
            if not path.exists():
                raise CommandError(
                    f"Arquivo CSV não encontrado: {path}. "
                    f"Execute antes: python scripts/seed.py"
                )

        try:
            # Uma única transação para tudo: se qualquer linha falhar,nada é gravado (estações e observações são revertidas juntas).
            with transaction.atomic():
                stations_created, stations_updated = self.import_stations(
                    stations_path
                )
                obs_created, obs_updated = self.import_observations(
                    observations_path
                )

        # Captura erros de conversão de valores, colunas ausentes e violações das constraints dos models.
        except (ValueError, KeyError, IntegrityError) as error:
            raise CommandError(
                f"Erro durante a importação: {error}"
            ) from error

        # Exibe o resumo da importação no terminal.
        self.stdout.write(
            self.style.SUCCESS(
                "Importação concluída! "
                f"Estações: {stations_created} criadas, {stations_updated} atualizadas. "
                f"Observações: {obs_created} criadas, {obs_updated} atualizadas."
            )
        )

    def open_csv(self, path, required_columns):
        # Abre o CSV, valida o cabeçalho e devolve o arquivo e o leitor.
        file = path.open(mode="r", encoding="utf-8", newline="")
        reader = csv.DictReader(file)

        # Verifica se todas as colunas necessárias estão presentes.
        if not required_columns.issubset(reader.fieldnames or []):
            file.close()
            raise CommandError(
                f"{path.name} não contém todas as colunas necessárias: "
                f"{', '.join(sorted(required_columns))}."
            )

        return file, reader

    def import_stations(self, path):
        # Cria ou atualiza as estações conforme definido no seed.py.
        created_count = 0
        updated_count = 0

        file, reader = self.open_csv(path, STATION_COLUMNS)
        with file:
            for row in reader:
                # O id vem do seed, para que as observações apontem para a estação certa.
                _, created = Station.objects.update_or_create(
                    pk=int(row["id"]),
                    defaults={
                        "name": row["name"],
                        "river": row["river"],
                        "municipality": row["municipality"],
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        return created_count, updated_count

    def import_observations(self, path):
        # Cria ou atualiza as observações, vinculando-as às estações já importadas.
        created_count = 0
        updated_count = 0

        # Carrega as estações de uma vez, evitando uma consulta por linha.
        stations_by_id = Station.objects.in_bulk()

        file, reader = self.open_csv(path, OBSERVATION_COLUMNS)
        with file:
            # Começa em 2 porque a linha 1 é o cabeçalho.
            for line_number, row in enumerate(reader, start=2):

                # A estação deve ter sido criada antes pelo stations.csv.
                station = stations_by_id.get(int(row["station_id"]))
                if station is None:
                    raise CommandError(
                        f"Linha {line_number}: estação {row['station_id']} "
                        f"não existe em stations.csv."
                    )

                observed_at = self.parse_observed_at(
                    row["observed_at"], line_number
                )

                # Procura uma observação com a mesma estação, métrica e data/hora.
                # Se encontrar, atualiza os valores; caso contrário, cria um novo registro.
                _, created = Observation.objects.update_or_create(
                    station=station,
                    metric=row["metric"],
                    observed_at=observed_at,
                    defaults={
                        "value": float(row["value"]),
                        "unit": row["unit"],
                        "source": row["source"],
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        return created_count, updated_count

    def parse_observed_at(self, raw_value, line_number):
        # Converte o texto ISO 8601 em datetime, respeitando a configuração USE_TZ.
        observed_at = parse_datetime(raw_value)

        # Interrompe a importação se a data for inválida.
        if observed_at is None:
            raise CommandError(
                f"Linha {line_number}: data inválida: {raw_value}"
            )

        # Compatibiliza com o settings.py para evitar erros ou avisos de fuso horário.
        if settings.USE_TZ and timezone.is_naive(observed_at):
            observed_at = timezone.make_aware(observed_at, timezone.utc)
        elif not settings.USE_TZ and timezone.is_aware(observed_at):
            observed_at = timezone.make_naive(observed_at, timezone.utc)

        return observed_at