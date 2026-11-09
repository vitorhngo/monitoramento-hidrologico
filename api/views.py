from rest_framework import viewsets # viewsets para criar CRUD da API automaticamente
from monitoring.models import Station # modelo Station do app monitoring
from .serializers import StationSerializer # serializer para o modelo Station


# ViewSet para o recurso Station:
# - fornece endpoints padrão (list, retrieve, create, update, destroy) pelo ModelViewSet,
class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all().order_by('id') # queryset base, ordenado por id
    serializer_class = StationSerializer # serializer usado para (de)serializar Station
    http_method_names = ['get', 'head']