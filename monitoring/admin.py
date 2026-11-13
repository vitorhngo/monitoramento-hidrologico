from django.contrib import admin
from rest_framework.authtoken.models import Token
from .models import Station, Observation

admin.site.register(Station)
admin.site.register(Observation)
admin.site.register(Token)