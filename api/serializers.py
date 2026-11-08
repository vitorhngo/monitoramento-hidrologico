from rest_framework import serializers
from monitoring.models import Station


# Serializer para o modelo Station — converte instâncias <-> representações JSON/HTTP
class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__' # expõe todos os campos do modelo Station