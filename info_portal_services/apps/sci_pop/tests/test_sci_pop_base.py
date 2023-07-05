from django.core import management
from info_portal_services.generic.test_base import BaseAPITestCase
from apps.tags.models import Tags
from apps.subjects.models import Subjects


class BaseSciPopAPITestCase(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.subject = Subjects.objects.get(pk=1)
        self.tag = Tags.objects.get(pk=1)
        management.call_command(
            'loaddata',
            'apps/sci_pop/fixtures/testing_authors.json',
            verbosity=1,
        )
        management.call_command(
            'loaddata',
            'apps/sci_pop/fixtures/sci_pop_formats.json',
            verbosity=1,
        )
        management.call_command(
            'loaddata',
            'apps/sci_pop/fixtures/testing_SciPop.json',
            verbosity=1,
        )
        management.call_command(
            'loaddata',
            'apps/sci_pop/fixtures/testing_comments.json',
            verbosity=1,
        )
