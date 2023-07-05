from random import randint

from django.urls import reverse
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.subjects.models import Subjects


class ApiSubjectsTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.subject = Subjects.objects.get(id=1)

    def test_subjects_list(self):
        url = reverse("subjects-list-create")
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json[0].get("title"), self.subject.title)

    def test_subjects_create(self):
        url = reverse("subjects-list-create")
        title = f"Subjects_title_{randint(0, 512)}"
        data = {
            "title": title,
        }
        response = self.client.post(url, data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("title"), title)
        db_object = Subjects.objects.get(id=response_json.get("id"))
        self.assertEqual(data.get("title"), db_object.title)

    def test_subjects_retrieve(self):
        url = reverse("subjects-id-response", args=(self.subject.id,))
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), self.subject.title)

    def test_subjects_update(self):
        url = reverse("subjects-id-response", args=(self.subject.id,))
        title = f"Subjects_title_{randint(0, 512)}"
        data = {
            "title": title,
        }
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), title)
        self.subject.refresh_from_db()
        self.assertEqual(data.get("title"), self.subject.title)

    def test_subjects_delete(self):
        url = reverse("subjects-id-response", args=(self.subject.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Subjects.DoesNotExist):
            Subjects.objects.get(id=self.subject.id)
