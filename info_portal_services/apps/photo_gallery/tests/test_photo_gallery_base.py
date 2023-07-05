from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import management
from info_portal_services.generic.test_base import BaseAPITestCase
from apps.tags.models import Tags
from apps.subjects.models import Subjects


class BaseGalleryAPITestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.subject = Subjects.objects.get(pk=1)
        self.tag = Tags.objects.get(pk=1)
        management.call_command(
            'loaddata',
            'apps/photo_gallery/fixtures/testing_post.json',
            verbosity=1,
        )
        management.call_command(
            'loaddata',
            'apps/photo_gallery/fixtures/testing_comments.json',
            verbosity=1,
        )
        with open("info_portal_services/generic/testing_image.png", "rb") as f:
            self.testing_image = SimpleUploadedFile(
                name="testing_image.png",
                content=f.read(),
                content_type="image/png"
            )
