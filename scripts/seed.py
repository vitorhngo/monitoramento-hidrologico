import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


stations = [
    {
        "id": 1,
        "name": "Estação Aurora",
        "river": "Rio Aurora",
        "municipality": "Vila Aurora",
    },
    {
        "id": 2,
        "name": "Estação Vale Verde",
        "river": "Rio Verde",
        "municipality": "Vale Verde",
    },
    {
        "id": 3,
        "name": "Estação Campo Alto",
        "river": "Rio do Campo",
        "municipality": "Campo Alto",
    },
]

# Colunas dos arquivos CSV. 
STATION_FIELDS = ["id", "name", "river", "municipality"]
OBSERVATION_FIELDS = [
    "station_id",
    "metric",
    "observed_at",
    "value",
    "unit",
    "source",
]


def generate_observations(stations):
    # Gera observações sintéticas para cada estação e horário.
    observations = []

    # Arredonda o horário atual para a hora cheia, em UTC.
    now = datetime.now(timezone.utc)
    end_hour = now.replace(minute=0, second=0, microsecond=0)

    # Gera 73 horários: das últimas 72 horas até a hora atual arredondada.
    for index in range(73):
        # Formato ISO 8601 em UTC, terminado em "Z" (ex.: 2026-11-05T21:00:00.000Z).
        timestamp = (
            (end_hour - timedelta(hours=72 - index))
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )

        for station_index, station in enumerate(stations):
            # Simula o nível do rio, em metros.
            level = (
                1.05
                + station_index * 0.24
                + 0.08 * math.sin(index / 5 + station_index)
            )

            # Simula a intensidade da chuva, em milímetros por hora.
            rain = (
                0.4 + ((index + station_index) % 4) * 0.35
                if (index + station_index * 7) % 17 < 3
                else 0
            )

            observations.append({
                "station_id": station["id"],
                "metric": "level",
                "observed_at": timestamp,
                "value": round(level, 2),
                "unit": "m",
                "source": "synthetic",
            })

            observations.append({
                "station_id": station["id"],
                "metric": "rain",
                "observed_at": timestamp,
                "value": round(rain, 2),
                "unit": "mm/h",
                "source": "synthetic",
            })

    return observations

# Grava uma lista de dicionários em um CSV (UTF-8) e devolve o caminho do arquivo.
def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return path

# Responsável por exportar estações e observações para a pasta data, na raiz do projeto.
def export_csv(stations, observations):
    # Identifica a raiz do projeto, considerando que este script está dentro da pasta scripts.
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    stations_path = write_csv(
        data_dir / "stations.csv", STATION_FIELDS, stations
    )
    observations_path = write_csv(
        data_dir / "observations.csv", OBSERVATION_FIELDS, observations
    )

    return stations_path, observations_path


def main():
    observations = generate_observations(stations) # Gera as observações sintéticas para todas as estações definidas no seed.
    stations_path, observations_path = export_csv(stations, observations) # Exporta estações e observações para os CSVs da pasta data e recebe os caminhos gerados.

    # Exibe no terminal o local e a quantidade de registros de cada arquivo exportado.
    print(f"Estações exportadas: {stations_path} ({len(stations)} estações).")
    print(
        f"Observações exportadas: {observations_path} "
        f"({len(observations)} observações)."
    )


if __name__ == "__main__":
    main()