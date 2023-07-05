from random import randint

from django.urls import reverse
from rest_framework import status

from apps.news.models import News, PubReviews, ReviewActions
from info_portal_services.generic.test_base import BaseAPITestCase
from apps.status_model.models import StatusTypes

# TODO: update
# class ReviewsTestCase(BaseAPITestCase):
    #
    # def setUp(self) -> None:
    #     super().setUp()
    #     self.pub_status_approved = PubStatus.objects.create(
    #         status="approved",
    #     )
    #     self.pub_status_returned = PubStatus.objects.create(
    #         status="returned",
    #     )
    #     self.news = News.objects.create(
    #         title=f"News_title_{randint(0, 512)}",
    #         text=f"News_text_{randint(0, 512)}",
    #     )
    #     self.news_2 = News.objects.create(
    #         title=f"News_title_{randint(0, 512)}",
    #         text=f"News_text_{randint(0, 512)}",
    #     )
    #     self.review_action = ReviewActions.objects.create(
    #         name="approve",
    #     )
    #     self.review_action_return = ReviewActions.objects.create(
    #         name="return",
    #     )
    #     self.pub_review = PubReviews.objects.create(
    #         publication=self.news,
    #         action=self.review_action,
    #     )
    #
    # def tearDown(self) -> None:
    #     self.pub_review.delete()
    #     self.review_action_return.delete()
    #     self.review_action.delete()
    #     self.news_2.delete()
    #     self.news.delete()
    #     self.pub_status_returned.delete()
    #     self.pub_status_approved.delete()
    #     super().tearDown()
    #
    # def test_reviews_list(self):
    #     url = reverse("reviews")
    #     response = self.client.get(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.json()[0].get("publication"), self.pub_review.publication.id)
    #     self.assertEqual(response.json()[0].get("action"), self.pub_review.action.id)
    #
    # def test_reviews_create(self):
    #     url = reverse("reviews")
    #     comment = f"Review_comment_{randint(0, 512)}"
    #     data = {
    #         "publication": self.news_2.id,
    #         "action": self.review_action.id,
    #         "comment": comment,
    #     }
    #     response = self.client.post(url, data=data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.json().get("publication"), self.news_2.id)
    #     self.assertEqual(response.json().get("action"), self.review_action.id)
    #
    # def test_reviews_detail_read(self):
    #     url = reverse("reviews-detail", args=(self.pub_review.id,))
    #     publication = self.pub_review.publication.id
    #     action = self.pub_review.action.id
    #     response = self.client.get(url, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.json().get("publication"), publication)
    #     self.assertEqual(response.json().get("action"), action)

    # # TODO: clarify information about endpoint
    # def test_reviews_detail_update(self):
    #     url = reverse("reviews-detail", args=(self.pub_review.id,))
    #     data = {
    #         "????": "????",
    #     }
    #     response = self.client.put(url, data=data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # # TODO: clarify information about endpoint
    # def test_reviews_detail_partial_update(self):
    #     url = reverse("reviews-detail", args=(self.pub_review.id,))
    #     data = {
    #         "????": "????",
    #     }
    #     response = self.client.patch(url, data=data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_reviews_detail_delete(self):
    #     url = reverse("reviews-detail", args=(self.pub_review.id,))
    #     response = self.client.delete(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     with self.assertRaises(PubReviews.DoesNotExist):
    #         PubReviews.objects.get(id=self.pub_review.id)
