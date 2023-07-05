from random import randint

from django.urls import reverse
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.metadata_catalog.models import Services


class ServicesTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super(ServicesTestCase, self).setUp()
        self.service = Services.objects.get(pk=1)

    def test_services_list(self):
        url = reverse("layers-services")
        response = self.client.get(url, format='json')
        data = response.json()[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.service.name)
        self.assertEqual(data.get("description"), self.service.description)
        self.assertEqual(data.get("url"), self.service.url)
        self.assertEqual(data.get("service_type"), self.service.service_type)

    def test_services_create(self):
        url = reverse("layers-services")
        request_data = {
            "name": f"Test name {randint(0, 512)}",
            "description": f"Test description {randint(0, 512)}",
            "url": f"https://www.test{randint(0, 512)}.com",
            "service_type": f"Test service type {randint(0, 512)}",
        }
        response = self.client.post(url, data=request_data, format='json')
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data.get("name"), request_data.get("name"))
        self.assertEqual(response_data.get("description"), request_data.get("description"))
        self.assertEqual(response_data.get("url"), request_data.get("url"))
        self.assertEqual(response_data.get("service_type"), request_data.get("service_type"))

        db_object = Services.objects.get(id=response_data.get("id"))
        self.assertEqual(db_object.name, request_data.get("name"))
        self.assertEqual(db_object.description, request_data.get("description"))
        self.assertEqual(db_object.url, request_data.get("url"))
        self.assertEqual(db_object.service_type, request_data.get("service_type"))

    def test_services_retrieve(self):
        url = reverse("layers-services-id", args=(self.service.id,))
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.service.name)
        self.assertEqual(data.get("description"), self.service.description)
        self.assertEqual(data.get("url"), self.service.url)
        self.assertEqual(data.get("service_type"), self.service.service_type)

    def test_services_update(self):
        url = reverse("layers-services-id", args=(self.service.id,))
        request_data = {
            "name": f"Test name {randint(0, 512)}",
            "description": f"Test description {randint(0, 512)}",
            "url": f"https://www.test{randint(0, 512)}.com",
            "service_type": f"Test service type {randint(0, 512)}",
        }
        response = self.client.put(url, data=request_data, format='json')
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data.get("name"), request_data.get("name"))
        self.assertEqual(response_data.get("description"), request_data.get("description"))
        self.assertEqual(response_data.get("url"), request_data.get("url"))
        self.assertEqual(response_data.get("service_type"), request_data.get("service_type"))

        self.service.refresh_from_db()
        self.assertEqual(self.service.name, request_data.get("name"))
        self.assertEqual(self.service.description, request_data.get("description"))
        self.assertEqual(self.service.url, request_data.get("url"))
        self.assertEqual(self.service.service_type, request_data.get("service_type"))

    def test_services_delete(self):
        url = reverse("layers-services-id", args=(self.service.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Services.DoesNotExist):
            Services.objects.get(id=self.service.id)
