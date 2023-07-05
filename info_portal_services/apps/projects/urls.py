from django.urls import path

from .views import ProjectsListCreateAPIView, ProjectTypesListCreateAPIView, \
    ProjectsRUDAPIView, ProjectItemsListCreateAPIView, ProjectItemsRUDAPIView


urlpatterns = [
    path('projects/', ProjectsListCreateAPIView.as_view(), 
        name="projects-list-create"),
    path('projects/types', ProjectTypesListCreateAPIView.as_view(), 
        name="project-types-list-create"),
    path('projects/<int:pk>/', ProjectsRUDAPIView.as_view(), 
        name="projects-rud"),
    path('projects/<int:pk>/items', ProjectItemsListCreateAPIView.as_view(), 
        name="project-items-list-create"),
    path('projects/item-details/<int:pk>', ProjectItemsRUDAPIView.as_view(), 
        name="project-items-rud"),
]
