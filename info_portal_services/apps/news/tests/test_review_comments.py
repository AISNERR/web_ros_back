from random import randint

from django.urls import reverse
from rest_framework import status

from apps.news.models import News, PubReviews, ReviewActions, NewsReviewComments
from info_portal_services.generic.test_base import BaseAPITestCase


class ReviewCommentsTestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.news = News.objects.create(
            title=f"News_title_{randint(0, 512)}",
            text=f"News_text_{randint(0, 512)}",
        )
        self.review_action = ReviewActions.objects.get(name="approve")
        self.pub_review = PubReviews.objects.create(
            publication=self.news,
            action=self.review_action,
        )
        self.review_comment = NewsReviewComments.objects.create(
            comment=f"Review_comment_{randint(0, 512)}",
            news=self.news,
        )

    def test_review_comments_create(self):
        url = reverse("review-comments", args=(self.pub_review.id,))
        comment = f"Review-comment_{randint(0, 512)}"
        data = {
            "comment": comment
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get("comment"), comment)
        self.assertEqual(response.json().get("news"), self.pub_review.publication.id)

    def test_review_comments_get(self):
        url = reverse("review-comments", args=(self.pub_review.id,))

        response = self.client.get(url, format="json")
        response_json = response.json()[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("news"), self.pub_review.publication.id)
        self.assertEqual(response_json.get("comment"), self.review_comment.comment)
