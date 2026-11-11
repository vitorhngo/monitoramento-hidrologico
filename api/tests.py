from datetime import datetime, timezone

from rest_framework import status
from rest_framework.test import APITestCase

from monitoring.models import Observation, Station


class StationSummaryTests(APITestCase):
    def setUp(self):
        self.station = Station.objects.create(
            name="Estação Teste",
            river="Rio Teste",
            municipality="Município Teste",
        )
        self.url = f"/api/stations/{self.station.pk}/summary/"

    def create_observation(self, metric, value, unit, observed_at):
        return Observation.objects.create(
            station=self.station,
            metric=metric,
            value=value,
            unit=unit,
            observed_at=datetime.fromisoformat(observed_at).replace(
                tzinfo=timezone.utc
            ),
        )

    def test_summary_returns_station_and_latest_reading_of_each_metric(self):
        self.create_observation(
            Observation.Metric.LEVEL, 1.2, Observation.Unit.METERS,
            "2026-11-08T10:00:00",
        )
        self.create_observation(
            Observation.Metric.LEVEL, 1.7, Observation.Unit.METERS,
            "2026-11-09T10:00:00",
        )
        self.create_observation(
            Observation.Metric.RAIN, 3.5, Observation.Unit.MM_PER_HOUR,
            "2026-11-09T09:00:00",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_simulated"])
        self.assertEqual(response.data["station"]["river"], "Rio Teste")
        self.assertEqual(response.data["station"]["municipality"], "Município Teste")
        self.assertEqual(response.data["latest_readings"]["level"]["value"], 1.7)
        self.assertEqual(response.data["latest_readings"]["level"]["unit"], "m")
        self.assertEqual(response.data["latest_readings"]["rain"]["value"], 3.5)
        self.assertEqual(response.data["latest_readings"]["rain"]["unit"], "mm/h")

    def test_summary_returns_null_when_a_metric_has_no_observations(self):
        self.create_observation(
            Observation.Metric.LEVEL, 1.2, Observation.Unit.METERS,
            "2026-11-09T10:00:00",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["latest_readings"]["rain"])

    def test_summary_returns_null_when_station_has_no_observations(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["latest_readings"]["level"])
        self.assertIsNone(response.data["latest_readings"]["rain"])

    def test_summary_returns_404_for_unknown_station(self):
        response = self.client.get("/api/stations/999999/summary/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
