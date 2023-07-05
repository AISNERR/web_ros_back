from random import randint

from django.urls import reverse
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.tags.models import Tags


class ApiTagsTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.tag = Tags.objects.get(id=1)

    def test_tags_list(self):
        url = reverse("tags-list-create")
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json[0].get("title"), self.tag.title)

    def test_tags_create(self):
        url = reverse("tags-list-create")
        title = f"Tags_title_{randint(0, 512)}"
        data = {
            "title": title,
        }
        response = self.client.post(url, data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("title"), title)
        db_object = Tags.objects.get(id=response_json.get("id"))
        self.assertEqual(data.get("title"), db_object.title)

    def test_tag_retrieve(self):
        url = reverse("tags-id-response", args=(self.tag.id,))
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), self.tag.title)

    def test_tags_update(self):
        url = reverse("tags-id-response", args=(self.tag.id,))
        title = f"Tags_title_{randint(0, 512)}"
        data = {
            "title": title,
        }
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), title)
        self.tag.refresh_from_db()
        self.assertEqual(data.get("title"), self.tag.title)

    def test_tags_delete(self):
        url = reverse("tags-id-response", args=(self.tag.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Tags.DoesNotExist):
            Tags.objects.get(id=self.tag.id)
