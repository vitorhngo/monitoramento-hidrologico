from django.db import models
from django.db.models import Q


class Station(models.Model):
    # Estação hidrológica
    id = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=120)
    river = models.CharField(max_length=120)
    municipality = models.CharField(max_length=120)

    class Meta:
        ordering = ["id"]
        constraints = [
            # Garante que o seed não duplique estações
            models.UniqueConstraint(
                fields=["name", "river", "municipality"],
                name="uniq_station_name_river_municipality",
            ),
        ]

    def __str__(self):
        # Retorna a representação textual da estação, no formato 'Nome (Rio - Município)'.
        # Não afeta o banco de dados nem o JSON da API.
        return f"{self.name} ({self.river} - {self.municipality})"


class Observation(models.Model):
    # Observação sintética de nível ou chuva de uma estação

    class Metric(models.TextChoices):
        LEVEL = "level", "Nível"
        RAIN = "rain", "Chuva"

    class Unit(models.TextChoices):
        METERS = "m", "metros"
        MM_PER_HOUR = "mm/h", "milímetros por hora"

    class Source(models.TextChoices):
        SYNTHETIC = "synthetic", "Sintético"

    # Chave estrangeira para a estação
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="observations",
    )
    # Sempre armazenado e exibido em formato 'UTC'
    observed_at = models.DateTimeField()
    value = models.FloatField()
    metric = models.CharField(max_length=10, choices=Metric.choices)
    unit = models.CharField(max_length=10, choices=Unit.choices)
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.SYNTHETIC,
    )

    class Meta:
        ordering = ["observed_at", "id"]
        indexes = [
            # Acelera o histórico filtrado por estação, métrica e período
            models.Index(
                fields=["station", "metric", "observed_at"],
                name="idx_obs_station_metric_time",
            ),
        ]

        constraints = [
            # Seed idempotente, sem observações duplicadas
            models.UniqueConstraint(
                fields=["station", "metric", "observed_at"],
                name="uniq_obs_station_metric_time",
            ),

            # Métricas com apenas 'level' e 'rain'
            models.CheckConstraint(
                condition=Q(metric__in=["level", "rain"]),
                name="chk_obs_metric_valid",
            ),

            # Unidade coerente com a métrica
            models.CheckConstraint(
                condition=(
                    Q(metric="level", unit="m")
                    | Q(metric="rain", unit="mm/h")
                ),
                name="chk_obs_metric_unit_match",
            ),
        ]

    def __str__(self):
        # Representação legível da observação: 'estação | métrica | valor unidade @ horário'.
        return (
            f"{self.station_id} | {self.metric} | "
            f"{self.value} {self.unit} @ {self.observed_at.isoformat()}"
        )
