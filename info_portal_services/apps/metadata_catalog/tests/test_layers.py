from random import randint

from django.core import management
from django.urls import reverse
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.metadata_catalog.models import Layers, LayerGroups, LayerTypes, Services


class MetadataCatalogTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super(MetadataCatalogTestCase, self).setUp()
        self.layer_group = LayerGroups.objects.get(pk=1)
        self.layer_type = LayerTypes.objects.get(pk=1)
        self.service = Services.objects.get(pk=1)
        management.call_command(
            'loaddata',
            'apps/metadata_catalog/fixtures/layer_test_data.json',
            verbosity=1,
        )
        self.layer = Layers.objects.get(pk=1)

    def test_layers_list(self):
        url = reverse("layers")
        response = self.client.get(url, format='json')
        data = response.json()[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.layer.name)
        self.assertEqual(data.get("description"), self.layer.description)
        self.assertEqual(data.get("visible"), self.layer.visible)
        self.assertEqual(data.get("layer_type_id").get("id"), self.layer.layer_type_id.id)
        self.assertEqual(data.get("layer_group_id").get("id"), self.layer.layer_group_id.id)
        self.assertEqual(data.get("service_id").get("id"), self.layer.service_id.id)
        self.assertEqual(data.get("created_by").get("id"), self.app_admin.id)

    def test_layers_create(self):
        url = reverse("layers")
        request_data = {
            "name": f"Test name {randint(0, 512)}",
            "description": f"Test description {randint(0, 512)}",
            "url": f"https://www.test{randint(0, 512)}.com",
            "visible": True,
            "layer_type_id": self.layer_type.id,
            "layer_group_id": self.layer_group.id,
            "service_id": self.service.id,
        }
        response = self.client.post(url, data=request_data, format='json')
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data.get("name"), request_data.get("name"))
        self.assertEqual(response_data.get("description"), request_data.get("description"))
        self.assertEqual(response_data.get("visible"), request_data.get("visible"))
        self.assertEqual(response_data.get("layer_type_id"), request_data.get("layer_type_id"))
        self.assertEqual(response_data.get("layer_group_id"), request_data.get("layer_group_id"))
        self.assertEqual(response_data.get("service_id"), request_data.get("service_id"))

        db_object = Layers.objects.get(id=response_data.get("id"))
        self.assertEqual(db_object.name, request_data.get("name"))
        self.assertEqual(db_object.description, request_data.get("description"))
        self.assertEqual(db_object.visible, request_data.get("visible"))
        self.assertEqual(db_object.layer_type_id.id, request_data.get("layer_type_id"))
        self.assertEqual(db_object.layer_group_id.id, request_data.get("layer_group_id"))
        self.assertEqual(db_object.service_id.id, request_data.get("service_id"))
        self.assertNotEqual(db_object.created_at, None)
        self.assertEqual(db_object.created_by.id, self.app_admin.id)

    def test_layers_retrieve(self):
        url = reverse("layers-id", args=(self.layer.id,))
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.layer.name)
        self.assertEqual(data.get("description"), self.layer.description)
        self.assertEqual(data.get("visible"), self.layer.visible)
        self.assertEqual(data.get("layer_type_id").get("id"), self.layer.layer_type_id.id)
        self.assertEqual(data.get("layer_group_id").get("id"), self.layer.layer_group_id.id)
        self.assertEqual(data.get("service_id").get("id"), self.layer.service_id.id)
        self.assertEqual(data.get("created_by").get("id"), self.app_admin.id)

    def test_layers_update(self):
        url = reverse("layers-id", args=(self.layer.id,))
        request_data = {
            "name": f"Test name {randint(0, 512)}",
            "description": f"Test description {randint(0, 512)}",
            "url": f"https://www.test{randint(0, 512)}.com",
            "visible": False,
            "layer_type_id": self.layer_type.id,
            "layer_group_id": self.layer_group.id,
            "service_id": self.service.id,
        }
        response = self.client.put(url, data=request_data, format='json')
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data.get("name"), request_data.get("name"))
        self.assertEqual(response_data.get("description"), request_data.get("description"))
        self.assertEqual(response_data.get("visible"), request_data.get("visible"))
        self.assertEqual(response_data.get("url"), request_data.get("url"))
        self.assertEqual(response_data.get("layer_type_id"), request_data.get("layer_type_id"))
        self.assertEqual(response_data.get("layer_group_id"), request_data.get("layer_group_id"))
        self.assertEqual(response_data.get("service_id"), request_data.get("service_id"))

        self.layer.refresh_from_db()
        self.assertEqual(self.layer.name, request_data.get("name"))
        self.assertEqual(self.layer.description, request_data.get("description"))
        self.assertEqual(self.layer.visible, request_data.get("visible"))
        self.assertEqual(self.layer.url, request_data.get("url"))
        self.assertEqual(self.layer.layer_type_id.id, request_data.get("layer_type_id"))
        self.assertEqual(self.layer.layer_group_id.id, request_data.get("layer_group_id"))
        self.assertEqual(self.layer.service_id.id, request_data.get("service_id"))
        self.assertNotEqual(self.layer.created_at, None)
        self.assertNotEqual(self.layer.updated_at, None)
        self.assertEqual(self.layer.created_by.id, self.app_admin.id)

    def test_layers_delete(self):
        url = reverse("layers-id", args=(self.layer.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Layers.DoesNotExist):
            Layers.objects.get(id=self.layer.id)
