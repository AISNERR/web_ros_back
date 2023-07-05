import json

from django.core import management
from django.core.files.uploadedfile import SimpleUploadedFile

from info_portal_services.generic.test_base import BaseAPITestCase
from apps.events.models import *


class EventsBaseAPITestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        management.call_command(
            'loaddata',
            'apps/events/fixtures/event_different_statuses_events.json',
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

        self.event_admin_published = Events.objects.get(pk=106)

        self.event_user_1_created = Events.objects.get(pk=121)
        self.event_user_1_ready_for_review = Events.objects.get(pk=122)
        self.event_user_1_review = Events.objects.get(pk=123)
        self.event_user_1_declined = Events.objects.get(pk=124)
        self.event_user_1_returned = Events.objects.get(pk=125)
        self.event_user_1_published = Events.objects.get(pk=126)
        self.event_user_1_archived = Events.objects.get(pk=127)

        self.event_type = EventTypes.objects.get(pk=1)
        self.event_format = EventFormats.objects.get(pk=1)
        self.subject = Subjects.objects.get(pk=1)
        self.tag = Tags.objects.get(pk=1)

        self.log_out()
