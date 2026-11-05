import csv
import math

from datetime import datetime, timedelta, timezone
from pathlib import Path


# Estações utilizadas na geração dos dados sintéticos
stations = [
    {
        "id": "EST-01",
        "name": "Estação Aurora",
        "river": "Rio Aurora",
        "municipality": "Vila Aurora",
    },
    {
        "id": "EST-02",
        "name": "Estação Vale Verde",
        "river": "Rio Verde",
        "municipality": "Vale Verde",
    },
    {
        "id": "EST-03",
        "name": "Estação Campo Alto",
        "river": "Rio do Campo",
        "municipality": "Campo Alto",
    },
]


def generate_observations(stations):
    """Gera observações sintéticas para cada estação e horário."""
    observations = []

    # Arredonda o horário atual para a hora cheia, em UTC.
    now = datetime.now(timezone.utc)
    end_hour = now.replace(minute=0, second=0, microsecond=0)

    # Gera 73 horários: das últimas 72 horas até a hora atual arredondada.
    for index in range(73):
        timestamp = (
            end_hour - timedelta(hours=72 - index)
        ).isoformat(timespec="milliseconds").replace("+00:00", "Z")

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



def export_csv(observations):
    """Exporta as observações para a pasta data na raiz do projeto."""

    # Identifica a raiz do projeto, considerando que este script está localizado dentro da pasta scripts.
    base_dir = Path(__file__).resolve().parent.parent

    # Define a pasta e o nome do arquivo CSV.
    output_path = base_dir / "data" / "observations.csv"

    # Cria a pasta data caso ela ainda não exista.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Define as colunas que serão exportadas.
    fieldnames = [
        "station_id",
        "metric",
        "observed_at",
        "value",
        "unit",
        "source",
    ]

    # Abre o arquivo e grava os dados no formato CSV.
    with output_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(observations)

    return output_path



def main():
    observations = generate_observations(stations)
    output_path = export_csv(observations)

    print(
        f"Arquivo CSV gerado com sucesso: {output_path} "
        f"({len(observations)} observações)."
    )


if __name__ == "__main__":
    main()
