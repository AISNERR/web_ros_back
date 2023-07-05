import json
from random import randint

from django.urls import reverse
from django.core import management
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.events.models import *


class TestEventsModerator(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        management.call_command(
            'loaddata',
            'apps/events/fixtures/event_different_statuses_events.json',
            verbosity=1,
        )
        management.call_command(
            'loaddata',
            'apps/events/fixtures/events_comments.json',
            verbosity=1,
        )
        with open("apps/events/fixtures/event_different_statuses_events.json") as f:
            self.fixtures_data = json.load(f)
        self.fixtures_info = {
            "amount": 28,
            "different users": 4,
            "status types": 7,
            "own": 7,
        }
        with open("info_portal_services/generic/testing_image.png", "rb") as f:
            self.testing_image = SimpleUploadedFile(
                name="testing_image.png",
                content=f.read(),
                content_type="image/png"
            )

        self.authenticate(self.app_moderator)

        self.event_created_by_user = Events.objects.get(pk=121)
        self.event_by_user_ready_for_review = Events.objects.get(pk=122)
        self.event_review_by_user = Events.objects.get(pk=123)
        self.event_published_by_user = Events.objects.get(pk=126)
        self.event_created_by_moder = Events.objects.get(pk=111)
        self.event_published_by_moder = Events.objects.get(pk=116)
        self.event_comment = EventModeratorComments.objects.get(pk=1)
        self.event_type = EventTypes.objects.get(pk=1)
        self.event_format = EventFormats.objects.get(pk=1)
        # write

    def test_published_events_list(self):
        url = reverse("events-list-create")
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json[2].get("title"), self.event_published_by_user.title)

    def test_create_event(self):
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

    def test_get_managing_events(self):
        url = reverse("events-detailed")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), self.fixtures_info.get("amount"))
        self.assertContains(response, "event_comments")
        self.assertContains(response, "event_status")

    def test_retrieve_event(self):
        url = reverse("events-rud", args=(self.event_published_by_moder.id,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), self.event_published_by_moder.title)

    def test_update_event(self):
        url = reverse("events-rud", args=(self.event_created_by_moder.id,))
        initial_data = {
            "title": self.event_created_by_moder.title,
            "image": self.event_created_by_moder.image,
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

    def test_update_access_to_user_event(self):
        url = reverse("events-rud", args=(self.event_created_by_user.id,))
        data = {}
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event(self):
        url = reverse("events-rud", args=(self.event_created_by_moder.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Events.DoesNotExist):
            Events.objects.get(id=self.event_created_by_moder.id)

    def test_delete_access_to_user_event(self):
        url = reverse("events-rud", args=(self.event_created_by_user.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_event_detail(self):
        url = reverse("events-info", args=(self.event_created_by_user.id,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), self.event_created_by_user.title)

    def test_send_event_to_review(self):
        url = reverse("events-send-to-review", args=(self.event_created_by_moder.id,))
        initial_data = {
            "event_status": 1
        }
        data = {}
        response = self.client.put(url, data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.event_created_by_moder.event_status, initial_data.get("event_status"))
        self.assertEqual(response_json.get("status"), 2)

    def test_access_send_user_event_to_review(self):
        url = reverse("events-send-to-review", args=(self.event_created_by_user.id,))
        data = {}
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_moderate_access_event(self):
        url = reverse("events-status-moderation", args=(self.event_created_by_user.id,))
        data = {}
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_ready_for_review_status(self):
        url = reverse("events-info", args=(self.event_by_user_ready_for_review.id,))
        initial_data = {
            "event_status": self.event_by_user_ready_for_review.event_status.id
        }
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.json().get("event_status"), initial_data.get("event_status"))

    def test_moderate_event(self):
        url = reverse("events-status-moderation", args=(self.event_review_by_user.id,))
        data = {
            "event_status": 5,
            "comment": f"testing comment_{randint(0, 512)}"
        }
        response = self.client.put(url, data=data, format='json')
        self.event_review_by_user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.event_review_by_user.event_status.id, data.get("event_status"))
        url = reverse("events-info", args=(self.event_review_by_user.id,))
        response = self.client.get(url, format="json")
        self.assertContains(response, text=data.get("comment"))

    def test_events_types_get(self):
        url = reverse("events-types")
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0].get("event_type"), self.event_type.event_type)

    def test_events_types_create(self):
        url = reverse("events-types")
        data = {}
        response = self.client.post(url, data=data, format='json')
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_events_formats_get(self):
        url = reverse("events-formats")
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0].get("event_format"), self.event_format.event_format)

    def test_events_formats_create(self):
        url = reverse("events-formats")
        data = {}
        response = self.client.post(url, data=data, format='json')
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testing_add_comments(self):
        url = reverse("events-admin-moderation")
        data = {
            "comment": "тестовый комментарий",
            "event":     self.event_created_by_user.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.post(url, data=data, format='json')
        self.event_created_by_user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url, format="json")
        self.assertContains(response, text=data.get("comment"))

    def testing_update_comments(self):
        url = reverse("events-admin-moderation-update", args=(self.event_comment.id,))
        data = {
            "comment": "тестовый комментарий",
            "event":     self.event_created_by_user.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = reverse("events-info", args=(self.event_created_by_user.id,))
        response = self.client.get(url, format="json")
        self.assertContains(response, text=data.get("comment"))
