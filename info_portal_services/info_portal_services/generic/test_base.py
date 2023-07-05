from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

User = get_user_model()


class BaseAPITestCase(APITestCase):
    fixtures = [
        # general
        'apps/subjects/fixtures/subjects.json',
        'apps/tags/fixtures/tags.json',
        'apps/status_model/fixtures/status_types.json',

        # news
        'apps/news/fixtures/pub_review_actions.json',

        # events
        'apps/events/fixtures/events_formats.json',
        'apps/events/fixtures/events_types.json',

        # rss catalog
        'apps/rss_catalog/fixtures/rss_catalog_groups.json',
        'apps/rss_catalog/fixtures/rss_catalog_data.json',

        # metadata_catalog
        'apps/metadata_catalog/fixtures/layer_groups.json',
        'apps/metadata_catalog/fixtures/layer_types.json',
        'apps/metadata_catalog/fixtures/services.json',
    ]

    @classmethod
    def setUpTestData(cls):
        cls.app_admin = User.objects.create_superuser(
            id=1,
            username="App-admin",
            email="App-admin@example.com",
            password="App-admin-password",
        )
        cls.app_admin_group = Group.objects.create(name="app-admin")
        cls.app_admin_group.user_set.add(cls.app_admin)
        cls.app_moderator = User.objects.create_user(
            id=2,
            username="App-moderator",
            email="App-moderator@example.com",
            password="App-moderator-password",
        )
        cls.content_manager_1 = User.objects.create_user(
            id=3,
            username="Content-manager-1",
            email="Content-manager-1@example.com",
            password="Content-manager-password-1",
        )
        cls.content_manager_2 = User.objects.create_user(
            id=4,
            username="Content-manager-2",
            email="Content-manager-2@example.com",
            password="Content-manager-2-password",
        )

        cls.app_moderator_group = Group.objects.create(name="app-moderator")
        cls.app_moderator_group.user_set.add(cls.app_moderator)

    def setUp(self) -> None:
        self.authenticate(self.app_admin)

    def authenticate(self, user):
        self.client.force_authenticate(user=user)
        self.current_user = user

    def log_out(self):
        self.client.logout()
