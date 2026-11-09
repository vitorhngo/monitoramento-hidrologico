from datetime import timezone as dt_timezone

from rest_framework import serializers
from monitoring.models import Station, Observation


# Serializer para o modelo Station — converte instâncias <-> representações JSON/HTTP
class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__' # expõe todos os campos do modelo Station


# Serializer de um ponto da série histórica (uma leitura): horário em UTC + valor
class ObservationPointSerializer(serializers.ModelSerializer):
    # Força a saída em UTC (ISO 8601 terminando em 'Z'), independente do TIME_ZONE do projeto
    observed_at = serializers.DateTimeField(default_timezone=dt_timezone.utc)

    class Meta:
        model = Observation
        fields = ['observed_at', 'value']