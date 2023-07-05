from random import randint

from django.urls import reverse
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.metadata_catalog.models import LayerTypes


class LayerTypesTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super(LayerTypesTestCase, self).setUp()
        self.layer_type = LayerTypes.objects.get(pk=1)

    def test_layers_types_list(self):
        url = reverse("layers-types")
        response = self.client.get(url, format='json')
        data = response.json()[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.layer_type.name)

    def test_layers_types_create(self):
        url = reverse("layers-types")
        request_data = {
            "name": f"Test name {randint(0, 512)}",
        }
        response = self.client.post(url, data=request_data, format='json')
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data.get("name"), request_data.get("name"))

        db_object = LayerTypes.objects.get(id=response_data.get("id"))
        self.assertEqual(db_object.name, request_data.get("name"))

    def test_layers_types_retrieve(self):
        url = reverse("layers-types-id", args=(self.layer_type.id,))
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.layer_type.name)

    def test_layers_types_update(self):
        url = reverse("layers-types-id", args=(self.layer_type.id,))
        request_data = {
            "name": f"Test name {randint(0, 512)}",
        }
        response = self.client.put(url, data=request_data, format='json')
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data.get("name"), request_data.get("name"))

        self.layer_type.refresh_from_db()
        self.assertEqual(self.layer_type.name, request_data.get("name"))

    def test_layers_types_delete(self):
        url = reverse("layers-types-id", args=(self.layer_type.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(LayerTypes.DoesNotExist):
            LayerTypes.objects.get(id=self.layer_type.id)
