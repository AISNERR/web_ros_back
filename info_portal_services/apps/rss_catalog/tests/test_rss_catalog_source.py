from random import randint

from django.urls import reverse
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.rss_catalog.models import NewsRss, NewsRssGroups


class RssCatalogSourceTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super(RssCatalogSourceTestCase, self).setUp()
        self.rss_source = NewsRss.objects.get(pk=1)
        self.rss_group = NewsRssGroups.objects.get(pk=1)

    def test_rss_catalog_list(self):
        url = reverse("rss-sources")
        response = self.client.get(url, format='json')
        response_json = response.json()[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), self.rss_source.title)
        self.assertEqual(response_json.get("group"), self.rss_source.group.id)
        self.assertEqual(response_json.get("site"), self.rss_source.site)
        self.assertEqual(response_json.get("rss_source"), self.rss_source.rss_source)

    def test_rss_catalog_create(self):
        url = reverse("rss-sources")
        data = {
            "title": f"Test title {randint(0, 512)}",
            "group": self.rss_group.id,
            "site": f"https://example{randint(0, 512)}.com/",
            "rss_source": f"https://example{randint(0, 512)}.com/rss",
        }
        response = self.client.post(url, data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("title"), data.get("title"))
        self.assertEqual(response_json.get("group"),  data.get("group"))
        self.assertEqual(response_json.get("site"),  data.get("site"))
        self.assertEqual(response_json.get("rss_source"),  data.get("rss_source"))
        self.assertEqual(response_json.get("created_by").get("id"), self.current_user.id)

        db_object = NewsRss.objects.get(id=response_json.get("id"))
        self.assertEqual(data.get("site"), db_object.site)
        self.assertEqual(data.get("title"), db_object.title)
        self.assertEqual(data.get("group"), db_object.group.id)
        self.assertEqual(data.get("rss_source"), db_object.rss_source)

    def test_rss_catalog_retrieve(self):
        url = reverse("rss-sources-id", args=(self.rss_source.id,))
        response = self.client.get(url, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.rss_source.title, response_json.get("title"))
        self.assertEqual(self.rss_source.group.id, response_json.get("group"))
        self.assertEqual(self.rss_source.site, response_json.get("site"))
        self.assertEqual(self.rss_source.rss_source, response_json.get("rss_source"))

    def test_rss_catalog_update(self):
        url = reverse("rss-sources-id", args=(self.rss_source.id,))
        data = {
            "title": f"Test title {randint(0, 512)}",
            "group": self.rss_source.group.id,
            "site": "https://example.com/",
            "rss_source": "https://example.com/rss",
        }
        response = self.client.put(url, data=data, format='json')
        self.rss_source.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), data.get("title"))
        self.assertEqual(self.rss_source.title, data.get("title"))
        self.assertEqual(self.rss_source.group.id, data.get("group"))
        self.assertEqual(self.rss_source.site, data.get("site"))
        self.assertEqual(self.rss_source.rss_source, data.get("rss_source"))

    def test_rss_catalog_delete(self):
        url = reverse("rss-sources-id", args=(self.rss_source.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(NewsRss.DoesNotExist):
            NewsRss.objects.get(id=self.rss_source.id)
