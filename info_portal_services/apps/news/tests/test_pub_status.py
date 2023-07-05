from django.urls import reverse
from rest_framework import status

from apps.status_model.models import StatusTypes
from info_portal_services.generic.test_base import BaseAPITestCase


class PubStatusTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.pub_status = StatusTypes.objects.get(id=1)

    def test_statuses_list(self):
        url = reverse("statuses")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0].get("status"), self.pub_status.status)
