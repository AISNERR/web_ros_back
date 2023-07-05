from random import randint

from django.urls import reverse
from rest_framework import status

from apps.events.models import Events
from .test_events_base import EventsBaseAPITestCase


class TestEventsCommonUser(EventsBaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.not_created_events = [
            self.event_user_1_ready_for_review.id,
            self.event_user_1_review.id,
            self.event_user_1_declined.id,
            self.event_user_1_returned.id,
            self.event_user_1_published.id,
            self.event_user_1_archived.id,
        ]
        self.authenticate(self.content_manager_1)

    def test_events_create(self):
        url = reverse("events-list-create")
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
        response = self.client.post(url, data=data, format='multipart')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("title"), data.get("title"))

    def test_events_update(self):
        url = reverse("events-rud", args=(self.event_user_1_created.id,))
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
        self.event_user_1_created.refresh_from_db()
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), data.get("title"))
        self.assertEqual(self.event_user_1_created.title, response_json.get("title"))

    def test_events_update_not_created_status(self):
        manageable = self.not_created_events[:]
        manageable.pop(self.not_created_events.index(self.event_user_1_returned.id,))
        for event_id in manageable:
            url = reverse("events-rud", args=(event_id,))
            data = {}
            response = self.client.put(url, data=data, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_delete(self):
        url = reverse("events-rud", args=(self.event_user_1_created.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Events.DoesNotExist):
            Events.objects.get(id=self.event_user_1_created.id)

    def test_events_delete_status_not_created(self):
        for event_id in self.not_created_events:
            url = reverse("events-rud", args=(event_id,))
            response = self.client.delete(url, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_list(self):
        url = reverse("events-detailed")
        response = self.client.get(url, format="json")
        response_json = response.json()[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), self.event_user_1_created.title)
        self.assertEqual(response_json.get("description"), self.event_user_1_created.description)
        self.assertEqual(response_json.get("short_description"), self.event_user_1_created.short_description)
        self.assertEqual(response_json.get("place"), self.event_user_1_created.place)
        self.assertIn(str(self.event_user_1_created.date_start.time()), response_json.get("date_start"))
        self.assertIn(str(self.event_user_1_created.date_start.date()), response_json.get("date_start"))
        self.assertIn(str(self.event_user_1_created.date_end.time()), response_json.get("date_end"))
        self.assertIn(str(self.event_user_1_created.date_end.date()), response_json.get("date_end"))
        self.assertEqual(response_json.get("email"), self.event_user_1_created.email)
        self.assertEqual(response_json.get("event_source"), self.event_user_1_created.event_source)
        self.assertEqual(response_json.get("organizer"), self.event_user_1_created.organizer)
        self.assertEqual(response_json.get("address"), self.event_user_1_created.address)
        self.assertEqual(response_json.get("event_format").get("id"), self.event_user_1_created.event_format.id)
        self.assertEqual(response_json.get("event_type").get("id"), self.event_user_1_created.event_type.id)
        self.assertEqual(response_json.get("subject").get("id"), self.event_user_1_created.subject.id)
        self.assertEqual(response_json.get("created_by").get("id"), self.content_manager_1.id)
        self.assertEqual(response_json.get("tags")[0].get('id'), self.event_user_1_created.tags.all()[0].id)

    def test_events_retrieve_detail(self):
        url = reverse("events-info", args=(self.event_user_1_created.id,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), self.event_user_1_created.title)

    def test_events_send_to_review(self):
        url = reverse("events-send-to-review", args=(self.event_user_1_created.id,))
        initial_data = {
            "event_status": 1
        }
        data = {}
        response = self.client.put(url, data=data, format='json')
        self.event_user_1_created.refresh_from_db()
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.event_user_1_created.event_status, initial_data.get("event_status"))
        self.assertEqual(response_json.get("status"), 2)

    def test_events_moderate(self):
        url = reverse("events-status-moderation", args=(self.event_user_1_review.id,))
        data = {}
        response = self.client.put(url, data=data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_send_to_review_not_created(self):
        for event_id in self.not_created_events:
            url = reverse("events-send-to-review", args=(event_id,))
            response = self.client.put(url, format='json')
            self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_events_types_list(self):
        url = reverse("events-types")
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0].get("event_type"), self.event_type.event_type)

    def test_events_types_create(self):
        url = reverse("events-types")
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_types_retrieve(self):
        url = reverse("events-types-id", args=(self.event_type.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("event_type"), self.event_type.event_type)

    def test_events_types_update(self):
        url = reverse("events-types-id", args=(self.event_type.id,))
        data = {}
        response = self.client.put(url, data=data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_types_delete(self):
        url = reverse("events-types-id", args=(self.event_type.id,))
        response = self.client.delete(url, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_formats_list(self):
        url = reverse("events-formats")
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0].get("event_format"), self.event_format.event_format)

    def test_events_formats_create(self):
        url = reverse("events-formats")
        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_formats_retrieve(self):
        url = reverse("events-formats-id", args=(self.event_format.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("event_format"), self.event_format.event_format)

    def test_events_formats_update(self):
        url = reverse("events-formats-id", args=(self.event_format.id,))
        data = {}
        response = self.client.put(url, data=data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_formats_delete(self):
        url = reverse("events-formats-id", args=(self.event_format.id,))
        response = self.client.delete(url, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testing_add_comments(self):
        url = reverse("events-admin-moderation")
        data = {
            "comment": f"Test comment {randint(0, 512)}",
            "event":     self.event_user_1_created.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testing_add_comments_update(self):
        url = reverse("events-admin-moderation-update", args=(self.event_user_1_created.id,))
        data = {
            "comment": f"Test comment {randint(0, 512)}",
            "event":     self.event_user_1_created.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
