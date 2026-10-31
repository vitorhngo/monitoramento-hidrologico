
import os
import math
import django

from datetime import timedelta
from django.utils import timezone
from django.db import transaction

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

# Importar os models
from monitoramento.models import Station, Observation


# Dados das estações
stations = [
    {
        'id': 'EST-01',
        'name': 'Estação Aurora',
        'river': 'Rio Aurora',
        'municipality': 'Vila Aurora'
    },
    {
        'id': 'EST-02',
        'name': 'Estação Vale Verde',
        'river': 'Rio Verde',
        'municipality': 'Vale Verde'
    },
    {
        'id': 'EST-03',
        'name': 'Estação Campo Alto',
        'river': 'Rio do Campo',
        'municipality': 'Campo Alto'
    }
]


def seed():

    # Iniciar transação
    with transaction.atomic():

        # Inserir ou recuperar estações
        saved_stations = []

        for station in stations:
            obj, created = Station.objects.update_or_create(
                id=station['id'],
                defaults={
                    'name': station['name'],
                    'river': station['river'],
                    'municipality': station['municipality']
                }
            )

            saved_stations.append(obj)

        # Definir horário atual arredondado
        now = timezone.now()

        end_hour = now.replace(
            minute=0,
            second=0,
            microsecond=0
        )

        # Gerar 73 horários
        for index in range(73):

            timestamp = end_hour - timedelta(hours=72 - index)

            # Percorrer estações
            for station_index, station in enumerate(saved_stations):

                # Calcular nível do rio
                level = (
                    1.05
                    + station_index * 0.24
                    + 0.08 * math.sin(index / 5 + station_index)
                )

                # Calcular intensidade da chuva
                rain = (
                    0.4 + ((index + station_index) % 4) * 0.35
                    if (index + station_index * 7) % 17 < 3
                    else 0
                )

                # Inserir nível do rio
                Observation.objects.update_or_create(
                    station=station,
                    metric='level',
                    observed_at=timestamp,
                    defaults={
                        'value': round(level, 2),
                        'unit': 'm',
                        'source': 'synthetic'
                    }
                )

                # Inserir intensidade da chuva
                Observation.objects.update_or_create(
                    station=station,
                    metric='rain',
                    observed_at=timestamp,
                    defaults={
                        'value': round(rain, 2),
                        'unit': 'mm/h',
                        'source': 'synthetic'
                    }
                )


# Executar rotina de inicialização
if __name__ == '__main__':

    try:
        seed()

        # Consultar quantidade de observações
        counts = Observation.objects.count()

        # Exibir resultado
        print(
            f'Amostra simulada pronta '
            f'({counts} observações).'
        )

    except Exception as error:
        print(f'Erro ao gerar dados: {error}')
        raise
