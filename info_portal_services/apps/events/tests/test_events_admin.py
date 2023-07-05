from random import randint

from django.urls import reverse
from rest_framework import status

from apps.events.tests.test_events_moderator import TestEventsModerator
from apps.events.models import *


class TestEventsAdmin(TestEventsModerator):

    def setUp(self) -> None:
        super().setUp()
        self.authenticate(self.app_admin)

    def test_delete_access_to_user_event(self):
        url = reverse("events-rud", args=(self.event_created_by_user.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Events.DoesNotExist):
            Events.objects.get(id=self.event_created_by_user.id)

    def test_access_send_user_event_to_review(self):
        url = reverse("events-send-to-review", args=(self.event_created_by_user.id,))
        initial_data = {
            "event_status": 1
        }
        data = {}
        response = self.client.put(url, data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.event_created_by_user.event_status, initial_data.get("event_status"))
        self.assertEqual(response_json.get("status"), 2)

    def test_update_access_to_user_event(self):
        url = reverse("events-rud", args=(self.event_created_by_user.id,))
        initial_data = {
            "title": self.event_created_by_user.title,
            "image": self.event_created_by_user.image,
        }
        data = {
            "title": f"Testing title_{randint(0, 512)}",
            "description": "Some text",
            "short_description": "short_description of event",
            "place": "SomeCity, SomeWhere street",
            "date_start": "2022-01-01 00:00:00",
            "date_end": "2022-01-02 00:00:00",
            "email": "contact_email@example.com",
            "event_source": "https://www.example.com/",
            "organizer": "organizer name",
            "address": "",
            "image": self.testing_image,
            "event_format": 1,
            "event_type": 2,
            "subject": 3,
            "tags": [
                1,
                2
            ]
        }
        response = self.client.put(url, data=data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.json().get('title'), initial_data.get('title'))
        self.assertNotEqual(response.json().get('image'), initial_data.get('image'))

    def test_events_types_get(self):
        url = reverse("events-types")
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0]["event_type"], self.event_type.event_type)
        self.assertEqual(response.json()[0]["name"], self.event_type.name)

    def test_events_types_create(self):
        url = reverse("events-types")
        data = {
            "event_type": f"Testing type_{randint(0, 512)}",
            "name": "имя"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["event_type"], data["event_type"])
        self.assertEqual(response.json()["name"], data["name"])

    def test_events_types_retrieve(self):
        url = reverse("events-types-id", args=(self.event_type.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["event_type"], self.event_type.event_type)
        self.assertEqual(response.json()["name"], self.event_type.name)

    def test_events_types_update(self):
        url = reverse("events-types-id", args=(self.event_type.id,))
        data = {
            "event_type": f"Testing type_{randint(0, 512)}",
            "name": "имя"
        }
        response = self.client.put(url, data=data, format='json')
        self.event_type.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("event_type"), data.get("event_type"))
        self.assertEqual(self.event_type.event_type, data["event_type"])
        self.assertEqual(self.event_type.name, data["name"])

    def test_events_formats_get(self):
        url = reverse("events-formats")
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0]["event_format"], self.event_format.event_format)
        self.assertEqual(response.json()[0]["name"], self.event_format.name)

    def test_events_formats_create(self):
        url = reverse("events-formats")
        data = {
            "event_format": f"Testing format_{randint(0, 512)}",
            "name": "имя"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["event_format"], data["event_format"])
        self.assertEqual(response.json()["name"], data["name"])

    def test_events_formats_retrieve(self):
        url = reverse("events-formats-id", args=(self.event_format.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["event_format"], self.event_format.event_format)
        self.assertEqual(response.json()["name"], self.event_format.name)

    def test_events_formats_update(self):
        url = reverse("events-formats-id", args=(self.event_format.id,))
        data = {
            "event_format": f"Testing format_{randint(0, 512)}",
            "name": "имя"
        }
        response = self.client.put(url, data=data, format='json')
        self.event_format.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("event_format"), data.get("event_format"))
        self.assertEqual(self.event_format.event_format, data["event_format"])
        self.assertEqual(self.event_format.name, data["name"])

    def testing_add_comments_adm(self):
        url = reverse("events-admin-moderation")
        data = {
            "comment": "тестовый комментарий",
            "event":     self.event_created_by_user.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def testing_add_comments_update_adm(self):
        url = reverse("events-admin-moderation-update", args=(self.event_comment.id,))
        data = {
            "comment": "тестовый комментарий",
            "event":     self.event_created_by_user.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)