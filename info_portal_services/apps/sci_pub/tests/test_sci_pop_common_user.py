from random import randint
from rest_framework import status

from django.urls import reverse
from apps.photo_gallery.models import PostInGallery
from apps.sci_pop.models import SciPopModeratorComments, SciPop
from apps.sci_pop.tests.test_sci_pop_base import BaseSciPopAPITestCase


class ApiSciPopTestCase(BaseSciPopAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.sci_pop_comment = SciPopModeratorComments.objects.get(pk=1)
        self.authenticate(self.content_manager_1)

    def test_sci_pop_list(self):
        self.post = SciPop.objects.get(pk=137)
        url = reverse("sci-pop-list-create")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()[2]
        self.assertEqual(response_json.get("title"), self.post.title)
        self.assertEqual(response_json.get("description"), self.post.description)
        self.assertEqual(response_json.get("video"), self.post.video)
        self.assertEqual(response_json.get("format")["id"], self.post.format.id)
        self.assertEqual(response_json.get("created_by").get('id'), self.post.created_by.id)
        self.assertIn(str(self.post.created_at.time()), response_json.get("created_at"))
        self.assertIn(str(self.post.created_at.date()), response_json.get("created_at"))
        self.assertEqual(response_json.get("tags")[0].get('id'), self.post.tags.all()[0].id)
        self.assertEqual(response_json.get("subject").get("id"), self.post.subject.id)
        self.assertEqual(self.post.sci_pop_status.status, "published")

    def test_sci_pop_create(self):
        url = reverse("sci-pop-list-create")
        data = {
            "title": f"Sci_pop_title_{randint(0, 512)}",
            "description": f"Sci_pop_text_{randint(0, 512)}",
            "tag": ["1", "2"],
            "video": "https://www.youtube.com",
            "author": ["Valerii Kobzev", "Anna"],
            "subject": self.subject.id,

        }
        response = self.client.post(url, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data["format"] = 1
        response = self.client.post(url, data=data, format='multipart')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("title"), data.get("title"))
        self.assertEqual(response_json.get("description"), data.get("description"))
        self.assertEqual(response_json.get("tags")[0]["id"], int(data.get("tag")[0].strip()))
        self.assertEqual(response_json.get("authors")[0]["full_name"], data.get("author")[0])
        self.assertEqual(response_json.get("video"), data.get("video"))
        self.assertEqual(response_json.get("format"), data.get("format"))
        self.assertEqual(response_json.get("subject"), data.get("subject"))
        self.assertEqual(response_json.get("created_by")["id"], self.current_user.id)
        db_object = SciPop.objects.get(id=response_json.get("id"))
        self.assertEqual(db_object.title, data.get("title"))
        self.assertEqual(db_object.description, data.get("description"))
        self.assertEqual(db_object.tags.all()[0].id, int(data.get("tag")[0]))
        self.assertEqual(db_object.authors.all()[0].full_name, data.get("author")[0])
        self.assertEqual(db_object.video, data.get("video"))
        self.assertEqual(db_object.format.id, data.get("format"))
        self.assertEqual(db_object.subject.id, data.get("subject"))
        self.assertIn(str(db_object.created_at.time()), response_json.get("created_at"))
        self.assertIn(str(db_object.created_at.date()), response_json.get("created_at"))

    def test_sci_pop_forbidden(self):
        self.post = SciPop.objects.get(pk=137)
        url = reverse("sci-pop-rud", args=(self.post.id,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sci_pop_retrieve(self):
        self.post = SciPop.objects.get(pk=137)
        url = reverse("sci-pop-rud", args=(self.post.id,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post = SciPop.objects.get(pk=127)
        url = reverse("sci-pop-rud", args=(self.post.id,))
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), self.post.title)
        self.assertEqual(response_json.get("description"), self.post.description)
        self.assertEqual(response_json.get("created_by").get('id'), self.post.created_by.id)
        self.assertIn(str(self.post.created_at.time()), response_json.get("created_at"))
        self.assertIn(str(self.post.created_at.date()), response_json.get("created_at"))
        self.assertEqual(response_json.get("tags")[0].get('id'), self.post.tags.all()[0].id)
        self.assertEqual(response_json.get("subject").get("id"), self.post.subject.id)

    def test_sci_pop_update(self):
        self.post = SciPop.objects.get(pk=137)
        url = reverse("sci-pop-rud", args=(self.post.id,))
        response = self.client.get(url, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post = SciPop.objects.get(pk=121)
        url = reverse("sci-pop-rud", args=(121,))
        data = {
            "title": f"Sci_pop_title_{randint(0, 512)}",
            "description": f"Sci_pop_text_{randint(0, 512)}",
            "tag": ["1", "2"],
            "video": "https://www.youtube.com",
            "author": ["Valerii Kobzev", "Anna"],
            "subject": self.subject.id,

        }
        response = self.client.put(url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data["format"] = "2"
        response = self.client.put(url, data=data, format="multipart")
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), data.get("title"))
        self.assertEqual(response_json.get("description"), data.get("description"))
        self.assertEqual(response_json.get("video"), data.get("video"))
        self.assertEqual(len(response_json.get("tags")), len(data.get("tag")))
        self.assertEqual(response_json.get("tags")[0]["id"], int(data.get("tag")[0].strip()))
        self.assertEqual(len(response_json.get("authors")), len(data.get("author")))
        self.assertEqual(response_json.get("authors")[0]["full_name"], data.get("author")[0].strip())
        self.assertEqual(response_json.get("subject"), data.get("subject"))
        self.assertEqual(response_json.get("created_by").get("id"), self.current_user.id)

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, data.get("title"))
        self.assertEqual(self.post.description, data.get("description"))
        self.assertEqual(self.post.video, data.get("video"))
        self.assertEqual(len(self.post.tags.all()), len(data.get("tag")))
        self.assertEqual(self.post.tags.all()[0].id, int(data.get("tag")[0]))
        self.assertEqual(len(self.post.authors.all()), len(data.get("author")))
        self.assertEqual(self.post.authors.all()[0].full_name, data.get("author")[0].strip())
        self.assertEqual(self.post.subject.id, data.get("subject"))
        self.assertIn(str(self.post.created_at.time()), response_json.get("created_at"))
        self.assertIn(str(self.post.created_at.date()), response_json.get("created_at"))

    def test_sci_pop_delete_FORBIDDEN(self):
        self.post = SciPop.objects.get(pk=131)
        url = reverse("sci-pop-rud", args=(self.post.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sci_pop_delete(self):
        self.post = SciPop.objects.get(pk=121)
        url = reverse("sci-pop-rud", args=(self.post.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(PostInGallery.DoesNotExist):
            PostInGallery.objects.get(id=self.post.id)

    def test_sci_pop_to_review_NOT_FOUND(self):
        self.post = SciPop.objects.get(pk=131)
        url = reverse("sci-pop-send-to-review", args=(self.post.id,))
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_sci_pop_to_review(self):
        self.post = SciPop.objects.get(pk=121)
        url = reverse("sci-pop-send-to-review", args=(self.post.id,))
        response = self.client.put(url, format='json')
        response_json = response.json()
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.post.sci_pop_status.status, "ready_for_review")
        self.assertEqual(response_json.get("status"), 2)

    def test_sci_pop_moderate_retrieve(self):
        self.post = SciPop.objects.get(pk=122)
        url = reverse("sci-pop-info", args=(self.post.id,))
        response = self.client.get(url, format='json')
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.post.sci_pop_status.status, "review")

    def test_sci_pop_set_status(self):
        self.post = SciPop.objects.get(pk=123)
        url = reverse("sci-pop-status-moderation", args=(self.post.id,))
        data = {
            "sci_pop_status": 5,
            "comment": f"Возвращен на доработку"
        }
        response = self.client.put(url, data=data, format='json')
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(self.post.sci_pop_status.id, data.get("sci_pop_status"))

    def test_sci_pop_archiving(self):
        self.post = SciPop.objects.get(pk=104)
        url = reverse("sci-pop-archive", args=(self.post.id,))
        data = {
            "action": "put_in"
        }
        response = self.client.put(url, data=data, format='json')
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(self.post.sci_pop_status.status, "archived")

    def test_sci_pop_add_comments(self):
        self.post = SciPop.objects.get(pk=105)
        url = reverse("sci-pop-admin-moderation")
        data = {
            "comment": "На доработку",
            "sci_pop": self.post.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.post(url, data=data, format='json')
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sci_pop_update_comments(self):
        self.post = SciPop.objects.get(pk=104)
        url = reverse("sci-pop-admin-moderation-update", args=(self.sci_pop_comment.id,))
        data = {
            "comment": "тестовый комментарий",
            "sci_pop": self.post.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_managing_sci_pop(self):
        url = reverse("sci-pop-detailed")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()),
                         SciPop.objects.filter(created_by=self.content_manager_1.id).count())
        self.assertContains(response, "sci_pop_comments")
        self.assertContains(response, "sci_pop_status")
