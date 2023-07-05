from random import randint

from django.urls import reverse
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.metadata_catalog.models import LayerGroups


class LayerGroupsTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super(LayerGroupsTestCase, self).setUp()
        self.layer_group = LayerGroups.objects.get(pk=1)

    def test_layers_groups_list(self):
        url = reverse("layers-groups")
        response = self.client.get(url, format='json')
        data = response.json()[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.layer_group.name)
        self.assertEqual(data.get("description"), self.layer_group.description)
        self.assertEqual(data.get("visible"), self.layer_group.visible)

    def test_layers_groups_create(self):
        url = reverse("layers-groups")
        request_data = {
            "name": f"Test name {randint(0, 512)}",
            "description": f"Test description {randint(0, 512)}",
            "visible": True,
        }
        response = self.client.post(url, data=request_data, format='json')
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data.get("name"), request_data.get("name"))
        self.assertEqual(response_data.get("description"), request_data.get("description"))
        self.assertEqual(response_data.get("visible"), request_data.get("visible"))

        db_object = LayerGroups.objects.get(id=response_data.get("id"))
        self.assertEqual(db_object.name, request_data.get("name"))
        self.assertEqual(db_object.description, request_data.get("description"))
        self.assertEqual(db_object.visible, request_data.get("visible"))

    def test_layers_groups_retrieve(self):
        url = reverse("layers-groups-id", args=(self.layer_group.id,))
        response = self.client.get(url, format='json')
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.layer_group.name)
        self.assertEqual(data.get("description"), self.layer_group.description)
        self.assertEqual(data.get("visible"), self.layer_group.visible)

    def test_layers_groups_update(self):
        url = reverse("layers-groups-id", args=(self.layer_group.id,))
        request_data = {
            "name": f"Test name {randint(0, 512)}",
            "description": f"Test description {randint(0, 512)}",
            "visible": False,
        }
        response = self.client.put(url, data=request_data, format='json')
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data.get("name"), request_data.get("name"))
        self.assertEqual(response_data.get("description"), request_data.get("description"))
        self.assertEqual(response_data.get("visible"), request_data.get("visible"))

        self.layer_group.refresh_from_db()
        self.assertEqual(self.layer_group.name, request_data.get("name"))
        self.assertEqual(self.layer_group.description, request_data.get("description"))
        self.assertEqual(self.layer_group.visible, request_data.get("visible"))

    def test_layers_groups_delete(self):
        url = reverse("layers-groups-id", args=(self.layer_group.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(LayerGroups.DoesNotExist):
            LayerGroups.objects.get(id=self.layer_group.id)
