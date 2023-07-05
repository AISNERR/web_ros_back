from random import randint, uniform
from rest_framework import status

from django.urls import reverse
from apps.photo_gallery.models import PostInGallery, GalleryModeratorComments
from apps.photo_gallery.tests.test_photo_gallery_base import BaseGalleryAPITestCase


class ApiGalleryTestCase(BaseGalleryAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.photo_gallery_comment = GalleryModeratorComments.objects.get(pk=1)
        self.authenticate(self.content_manager_1)

    def test_gallery_list(self):
        self.post = PostInGallery.objects.get(pk=137)
        url = reverse("photo-gallery-list-create")
        response = self.client.get(url, format="json")
        response_json = response.json()[2]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), self.post.title)
        self.assertEqual(response_json.get("alt_text"), self.post.alt_text)
        self.assertEqual(response_json.get("created_by").get('id'), self.post.created_by.id)
        self.assertIn(str(self.post.created_at.time()), response_json.get("created_at"))
        self.assertIn(str(self.post.created_at.date()), response_json.get("created_at"))
        self.assertEqual(response_json.get("tags")[0].get('id'), self.post.tags.all()[0].id)
        self.assertEqual(response_json.get("subject").get("id"), self.post.subject.id)

    def test_gallery_create(self):
        url = reverse("photo-gallery-list-create")
        post_coordinates = [
            round(uniform(0, 60), 6),
            round(uniform(0, 60), 6)
        ]

        geo_json = '{"type":"Feature","geometry":{"type": "Point",'f'"coordinates":{post_coordinates}''},' \
                   '"properties":{}}'
        data = {
            "title": f"Gallery_post_title_{randint(0, 512)}",
            "alt_text": f"Gallery_text_{randint(0, 512)}",
            "tags": [
                self.tag.id
            ],
            "location": geo_json,
            "subject": self.subject.id,
            "image": self.testing_image
        }
        response = self.client.post(url, data=data, format='multipart')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("title"), data.get("title"))
        self.assertEqual(response_json.get("alt_text"), data.get("alt_text"))
        self.assertEqual(response_json.get("tags"), data.get("tags"))
        self.assertEqual(response_json.get("subject"), data.get("subject"))
        self.assertEqual(response_json.get("created_by").get("id"), self.current_user.id)
        db_object = PostInGallery.objects.get(id=response_json.get("id"))
        self.assertEqual(db_object.location.coordinates.x, post_coordinates[0])
        self.assertEqual(db_object.location.coordinates.y, post_coordinates[1])
        self.assertEqual(db_object.title, data.get("title"))
        self.assertEqual(db_object.alt_text, data.get("alt_text"))
        self.assertEqual(db_object.tags.all()[0].id, data.get("tags")[0])
        self.assertEqual(db_object.subject.id, data.get("subject"))
        self.assertIn(str(db_object.created_at.time()), response_json.get("created_at"))
        self.assertIn(str(db_object.created_at.date()), response_json.get("created_at"))

    def test_gallery_retrieve_forbidden(self):
        self.post = PostInGallery.objects.get(pk=137)
        url = reverse("photo-gallery-rud", args=(self.post.id,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_gallery_retrieve(self):
        self.post = PostInGallery.objects.get(pk=127)
        url = reverse("photo-gallery-rud", args=(self.post.id,))
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), self.post.title)
        self.assertEqual(response_json.get("alt_text"), self.post.alt_text)
        self.assertEqual(response_json.get("created_by").get('id'), self.post.created_by.id)
        self.assertIn(str(self.post.created_at.time()), response_json.get("created_at"))
        self.assertIn(str(self.post.created_at.date()), response_json.get("created_at"))
        self.assertEqual(response_json.get("tags")[0].get('id'), self.post.tags.all()[0].id)
        self.assertEqual(response_json.get("subject").get("id"), self.post.subject.id)

    def test_gallery_update(self):
        post_coordinates = [
            round(uniform(0, 60), 6),
            round(uniform(0, 60), 6)
        ]
        geo_json = '{"type":"Feature","geometry":{"type": "Point",'f'"coordinates":{post_coordinates}''},' \
                   '"properties":{}}'
        data = {
            "title": f"Gallery_post_title_{randint(0, 512)}",
            "alt_text": f"Gallery_text_{randint(0, 512)}",
            "tags": [
                self.tag.id
            ],
            "location": geo_json,
            "subject": self.subject.id,
        }
        self.post = PostInGallery.objects.get(pk=131)
        url = reverse("photo-gallery-rud", args=(131,))
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.post = PostInGallery.objects.get(pk=121)
        url = reverse("photo-gallery-rud", args=(121,))
        response = self.client.put(url, data=data, format="json")
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("title"), data.get("title"))
        self.assertEqual(response_json.get("alt_text"), data.get("alt_text"))
        self.assertEqual(response_json.get("tags"), data.get("tags"))
        self.assertEqual(response_json.get("subject"), data.get("subject"))
        self.assertEqual(response_json.get("created_by").get("id"), self.current_user.id)

        self.post.refresh_from_db()
        self.assertEqual(self.post.location.coordinates.x, post_coordinates[0])
        self.assertEqual(self.post.location.coordinates.y, post_coordinates[1])
        self.assertEqual(self.post.title, data.get("title"))
        self.assertEqual(self.post.alt_text, data.get("alt_text"))
        self.assertEqual(self.post.tags.all()[0].id, data.get("tags")[0])
        self.assertEqual(self.post.subject.id, data.get("subject"))
        self.assertIn(str(self.post.created_at.time()), response_json.get("created_at"))
        self.assertIn(str(self.post.created_at.date()), response_json.get("created_at"))

    def test_gallery_delete_FORBIDDEN(self):
        self.post = PostInGallery.objects.get(pk=131)
        url = reverse("photo-gallery-rud", args=(self.post.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_gallery_delete(self):
        self.post = PostInGallery.objects.get(pk=121)
        url = reverse("photo-gallery-rud", args=(self.post.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(PostInGallery.DoesNotExist):
            PostInGallery.objects.get(id=self.post.id)

    def test_gallery_to_review_NOT_FOUND(self):
        self.post = PostInGallery.objects.get(pk=131)
        url = reverse("photo-gallery-send-to-review", args=(self.post.id,))
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_gallery_to_review(self):
        self.post = PostInGallery.objects.get(pk=121)
        url = reverse("photo-gallery-send-to-review", args=(self.post.id,))
        response = self.client.put(url, format='json')
        response_json = response.json()
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.post.photo_gallery_status.status, "ready_for_review")
        self.assertEqual(response_json.get("status"), 2)

    def test_gallery_moderate_retrieve(self):
        self.post = PostInGallery.objects.get(pk=122)
        url = reverse("photo-gallery-info", args=(self.post.id,))
        response = self.client.get(url, format='json')
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.post.photo_gallery_status.status, "review")

    def test_gallery_moderate_set_status(self):
        self.post = PostInGallery.objects.get(pk=123)
        url = reverse("photo-gallery-status-moderation", args=(self.post.id,))
        data = {
            "photo_gallery_status": 5,
            "comment": f"Возвращен на доработку"
        }
        response = self.client.put(url, data=data, format='json')
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(self.post.photo_gallery_status.id, data.get("photo_gallery_status"))

    def test_gallery_archiving(self):
        self.post = PostInGallery.objects.get(pk=124)
        url = reverse("photo-gallery-archive", args=(self.post.id,))
        data = {
            "action": "put_in"
        }
        response = self.client.put(url, data=data, format='json')
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(self.post.photo_gallery_status.status, "archived")

    def testing_add_comments(self):
        self.post = PostInGallery.objects.get(pk=125)
        url = reverse("photo-gallery-admin-moderation")
        data = {
            "comment": "На доработку",
            "photo": self.post.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.post(url, data=data, format='json')
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def testing_update_comments(self):
        self.post = PostInGallery.objects.get(pk=104)
        url = reverse("photo-gallery-admin-moderation-update", args=(self.photo_gallery_comment.id,))
        data = {
            "comment": "тестовый комментарий",
            "photo":     self.post.id,
            "created_by": self.app_admin.id,
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_managing_gallery(self):
        url = reverse("photo-gallery-detailed")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()),
                         PostInGallery.objects.filter(created_by=self.content_manager_1.id).count())
        self.assertContains(response, "photo_gallery_comments")
        self.assertContains(response, "photo_gallery_status")
