from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets, status # viewsets para criar CRUD da API automaticamente
from rest_framework.decorators import action
from rest_framework.response import Response
from monitoring.models import Station, Observation # modelos do app monitoring
from .serializers import StationSerializer, ObservationPointSerializer

# Unidade de cada métrica (a mesma regra da constraint chk_obs_metric_unit_match do model)
UNIT_BY_METRIC = {
    Observation.Metric.LEVEL: Observation.Unit.METERS,
    Observation.Metric.RAIN: Observation.Unit.MM_PER_HOUR,
}

DEFAULT_HOURS = 24
MIN_HOURS = 1
MAX_HOURS = 72


# ViewSet para o recurso Station:
# - fornece endpoints padrão (list, retrieve, create, update, destroy) pelo ModelViewSet,
class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all().order_by('id') # queryset base, ordenado por id
    serializer_class = StationSerializer # serializer usado para (de)serializar Station
    http_method_names = ['get', 'head']

    # GET /api/stations/{id}/series/?metric=level&hours=24
    # Histórico de nível ('level') ou chuva ('rain') de uma estação.
    @action(detail=True, methods=['get'], url_path='series')
    def series(self, request, pk=None):
        station = self.get_object() # 404 automático se a estação não existe

        # Valida a métrica (obrigatória)
        metric = request.query_params.get('metric')
        if metric not in Observation.Metric.values:
            return Response(
                {'error': "Parâmetro 'metric' obrigatório e deve ser 'level' ou 'rain'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Valida a janela de horas (opcional, padrão 24, entre 1 e 72)
        try:
            hours = int(request.query_params.get('hours', DEFAULT_HOURS))
        except ValueError:
            hours = None
        if hours is None or not (MIN_HOURS <= hours <= MAX_HOURS):
            return Response(
                {'error': f"Parâmetro 'hours' deve ser um número inteiro entre {MIN_HOURS} e {MAX_HOURS}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Consulta via ORM (parametrizada), ordenada por horário; só devolve o que existe (sem inventar lacunas)
        since = timezone.now() - timedelta(hours=hours)
        observations = (
            station.observations
            .filter(metric=metric, observed_at__gte=since)
            .order_by('observed_at')
        )

        return Response({
            'station_id': station.id,
            'metric': metric,
            'unit': UNIT_BY_METRIC[metric],
            'hours': hours,
            'simulated': True, # dados fictícios (exigência do desafio)
            'source': Observation.Source.SYNTHETIC,
            'points': ObservationPointSerializer(observations, many=True).data,
        })
          
    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        station = self.get_object()
        latest_readings = {}

        for metric in (Observation.Metric.LEVEL, Observation.Metric.RAIN):
            observation = (
                Observation.objects.filter(station=station, metric=metric)
                .order_by("-observed_at", "-id")
                .first()
            )
            latest_readings[metric] = (
                {
                    "value": observation.value,
                    "unit": observation.unit,
                    "observed_at": observation.observed_at,
                }
                if observation is not None
                else None
            )

        return Response({
            "is_simulated": True,
            "station": self.get_serializer(station).data,
            "latest_readings": latest_readings,
        })