from random import randint

from django.urls import reverse
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.rss_catalog.models import NewsRssGroups


class RssCatalogGroupTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super(RssCatalogGroupTestCase, self).setUp()
        self.rss_group = NewsRssGroups.objects.get(pk=1)

    def test_rss_catalog_groups_list(self):
        url = reverse("rss-sources-groups")
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0].get("title"), self.rss_group.title)

    def test_rss_catalog_groups_create(self):
        url = reverse("rss-sources-groups")
        data = {
            "title": f"Test title {randint(0, 512)}",
        }
        response = self.client.post(url, data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("title"), data.get("title"))
        db_object = NewsRssGroups.objects.get(id=response_json.get("id"))
        self.assertEqual(data.get("title"), db_object.title)

    def test_rss_catalog_groups_retrieve(self):
        url = reverse("rss-sources-groups-id", args=(self.rss_group.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), self.rss_group.title)

    def test_rss_catalog_groups_update(self):
        url = reverse("rss-sources-groups-id", args=(self.rss_group.id,))
        data = {
            "title": f"Test title {randint(0, 512)}",
        }
        response = self.client.put(url, data=data, format='json')
        self.rss_group.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), data.get("title"))
        self.assertEqual(self.rss_group.title, data.get("title"))

    def test_rss_catalog_groups_delete(self):
        url = reverse("rss-sources-groups-id", args=(self.rss_group.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(NewsRssGroups.DoesNotExist):
            NewsRssGroups.objects.get(id=self.rss_group.id)
