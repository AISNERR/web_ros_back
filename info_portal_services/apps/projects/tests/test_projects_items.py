from django.urls import reverse
from django.core import management
from rest_framework import status

from info_portal_services.generic.test_base import BaseAPITestCase



class TestProjects(BaseAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.authenticate(self.content_manager_1)
        management.call_command(
            'loaddata',
            'apps/projects/tests/data/projects.json',
            verbosity=1,
        )

    def test_create_project(self):
        url = reverse("projects-list-create")
        data = {
            "project_type": 1,
            "title": "Test Project",
            "description": "Test Project Description"
        }
        response = self.client.post(url, data=data, format='json')
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("title"), data.get("title"))
        self.assertEqual(response_json.get("project_type"), data.get("project_type"))
        self.assertEqual(response_json.get(
            "description"), data.get("description"))

    def test_projects_list(self):
        url = reverse("projects-list-create")
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json[0].get("title"), "Test Project 1")

    def test_create_items(self):
        url = reverse("project-items-list-create", args=[1])
        data = {
            "item_type": "oilspillcontour",
            "project": 1,
            "geom": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            0.0,
                            0.0
                        ],
                        [
                            5.0,
                            5.0
                        ],
                        [
                            10.0,
                            0.0
                        ],
                        [
                            0.0,
                            0.0
                        ]
                    ]
                ]
            }
        }
        response = self.client.post(url, data=data, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json.get("item_type"), "oilspillcontour")

    def test_create_items(self):
        url = reverse("project-items-list-create", args=[1])
        url_update = reverse("project-items-rud", args=[1])
        data = {
            "item_type": "oilspillcontour",
            "project": 1,
            "geom": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            0.0,
                            0.0
                        ],
                        [
                            5.0,
                            5.0
                        ],
                        [
                            10.0,
                            0.0
                        ],
                        [
                            0.0,
                            0.0
                        ]
                    ]
                ]
            }
        }
        data_update = {
            "item_type": "oilspillcontour",
            "project": 1,
            "geom": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            0.0,
                            0.0
                        ],
                        [
                            6.0,
                            6.0
                        ],
                        [
                            10.0,
                            0.0
                        ],
                        [
                            0.0,
                            0.0
                        ]
                    ]
                ]
            }
        }
        
        response = self.client.post(url, data=data, format="json")
        response = self.client.put(url_update, data=data_update, format="json")
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json.get("geom"), data_update["geom"])