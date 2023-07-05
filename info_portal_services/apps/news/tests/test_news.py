from random import randint, uniform

from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.news.models import Tags, Subjects, News, ReviewActions
from apps.location.models import Location
from apps.status_model.models import StatusTypes


class ApiNewsTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.pub_status_approved = StatusTypes.objects.get(
            status="approved",
        )
        self.pub_status_created = StatusTypes.objects.get(
            status="created",
        )
        self.pub_status_declined = StatusTypes.objects.get(
            status="declined",
        )
        self.review_action_approve = ReviewActions.objects.get(
            name="approve",
        )
        self.subject = Subjects.objects.get(
            id=1,
        )
        self.tag = Tags.objects.get(
            id=1,
        )
        self.news_location = Location.objects.create(
            coordinates=Point(
                round(uniform(0, 1), 1),
                round(uniform(0, 1), 1),
            ),
        )
        self.news = News.objects.create(
            title=f"News_title_{randint(0, 512)}",
            text=f"News_text_{randint(0, 512)}",
            status=self.pub_status_approved,
            location=self.news_location,
            subject=self.subject,
            text_short=f"News_text_short{randint(0, 512)}"
        )

    def test_news_list(self):
        url = reverse("news")
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json[0].get("title"), self.news.title)
        self.assertEqual(response_json[0].get("text_short"), self.news.text_short)

    def test_news_create(self):
        url = reverse("news")
        title = f"News_title_{randint(0, 512)}"
        text = f"News_text_{randint(0, 512)}"
        text_short = f"News_text_short_{randint(0, 512)}"
        tags = [self.tag.id]
        post_coordinates = [
            round(uniform(0, 60), 6),
            round(uniform(0, 60), 6)
        ]
        geo_json = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": post_coordinates,
                "properties": {}
            }
        }
        data = {
            "title": title,
            "text": text,
            "tags": tags,
            "location": geo_json,
            "text_short": text_short
        }
        response = self.client.post(url, data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("title"), title)
        self.assertEqual(response_json.get("text"), text)
        self.assertEqual(response_json.get("tags"), tags)
        self.assertEqual(response_json.get("text_short"), text_short)

    def test_news_locations_list(self):
        url = reverse("news-locations")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json().get("features")[0].get("geometry").get("coordinates"),
            list(self.news_location.coordinates.tuple),
        )

    def test_news_locations_create(self):
        url = reverse("news-locations")
        coordinates = [
            round(uniform(0, 1), 1),
            round(uniform(0, 1), 1),
        ]
        data = {
            "coordinates": {
                "type": "Point",
                "coordinates":  coordinates,
            }
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get("geometry").get("coordinates"), coordinates)

    def test_news_status_update(self):
        url = reverse("news-status", args=(self.news.id,))
        p_status_id = self.pub_status_declined.id
        data = {
            "status": p_status_id
        }
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("status"), p_status_id)

    def test_news_detail_read(self):
        url = reverse("news-detail", args=(self.news.id,))
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), self.news.title)
        self.assertEqual(response_json.get("text"), self.news.text)
        self.assertEqual(response_json.get("text_short"), self.news.text_short)

    def test_news_detail_update(self):
        url = reverse("news-detail", args=(self.news.id,))
        title = f"New_title_{randint(0, 512)}"
        text = f"News_text_{randint(0, 512)}"
        text_short = f"News_text_short{randint(0, 512)}"
        tags = [self.tag.id]
        data = {
            "title": title,
            "text": text,
            "tags": tags,
            "text_short": text_short
        }
        response = self.client.put(url, data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), title)
        self.assertEqual(response_json.get("text"), text)
        self.assertEqual(response_json.get("tags"), tags)
        self.assertEqual(response_json.get("text_short"), text_short)

    def test_news_detail_delete(self):
        url = reverse("news-detail", args=(self.news.id,))
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(News.DoesNotExist):
            News.objects.get(id=self.news.id)

    def test_news_location_detail_read(self):
        url = reverse("news-locations-detail", args=(self.news_location.id,))
        coordinates = list(self.news.location.coordinates.tuple)
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("geometry").get("coordinates"), coordinates)

    def test_news_location_detail_update(self):
        url = reverse("news-locations-detail", args=(self.news_location.id,))
        coordinates = [
            round(uniform(0, 1), 1),
            round(uniform(0, 1), 1),
        ]
        data = {
            "coordinates": {
                "type": "Point",
                "coordinates": coordinates,
            }
        }
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("geometry").get("coordinates"), coordinates)

    def test_news_location_detail_delete(self):
        url = reverse("news-locations-detail", args=(self.news_location.id,))
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Location.DoesNotExist):
            Location.objects.get(id=self.news_location.id)
