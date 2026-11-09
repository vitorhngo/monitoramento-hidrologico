from rest_framework import viewsets # viewsets para criar CRUD da API automaticamente
from monitoring.models import Station, Observation # modelo Station do app monitoring
from .serializers import StationSerializer # serializer para o modelo Station
from rest_framework.decorators import action
from rest_framework.response import Response

# ViewSet para o recurso Station:
# - fornece endpoints padrão (list, retrieve, create, update, destroy) pelo ModelViewSet,
class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all().order_by('id') # queryset base, ordenado por id
    serializer_class = StationSerializer # serializer usado para (de)serializar Station
    http_method_names = ['get', 'head']

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