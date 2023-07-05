from django.db import models


class LayerGroups(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)
    visible = models.BooleanField(default=True)


class LayerTypes(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Services(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)
    service_type = models.CharField(max_length=255, blank=True)


class Layers(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)
    layer_type_id = models.ForeignKey(
        to=LayerTypes,
        on_delete=models.SET_NULL,
        related_name="layers_in_types",
        null=True
    )
    layer_group_id = models.ForeignKey(
        to=LayerGroups,
        related_name="layers_in_groups",
        on_delete=models.SET_NULL,
        null=True
    )
    service_id = models.ForeignKey(
        to=Services,
        on_delete=models.SET_NULL,
        related_name="layers_in_services",
        null=True
    )
    visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name="layers_created",
        null=True,
    )


def layers_tree_default():
    return dict()


class LayersViewSet(models.Model):
    name = models.CharField(max_length=255, unique=True)
    layers = models.ManyToManyField(
        to=Layers,
        related_name="viewset_in_layers",
    )
    layers_tree = models.JSONField(validators=[], default=layers_tree_default)

    def __str__(self):
        return (
            f"{self.__class__.__name__} object "
            f"(id: {self.id}) (name: {self.name}) (description: {self.description}) (url: {self.url}) "
            f"(visible: {self.visible} (layer_type_id: {self.layer_type_id}) (layer_group_id: {self.layer_group_id}) "
            f"(service_id: {self.service_id}) (created_at: {self.created_at}) (updated_at: {self.updated_at}) "
            f"(created_by: {self.created_by})"
        )

