from data_food_consortium.models import Enterprise
from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import ReadOnly
from djangoldp_custom_dfc.models.__base import baseModel
from djangoldp_custom_dfc.models.custom_service import Service


class EnterpriseExtension(baseModel):
    enterprise = models.ForeignKey(
        Enterprise, on_delete=models.CASCADE, related_name="extension"
    )
    services = models.ManyToManyField(Service, blank=True)
    published = models.BooleanField(default=False)

    class Meta(baseModel.Meta):
        verbose_name = _("Publication Status")
        verbose_name_plural = _("Publication Status")

        serializer_fields = baseModel.Meta.serializer_fields + [
            "published",
            "services",
        ]
        nested_fields = ["services"]
        rdf_type = "custom:Publication"
        permission_classes = [ReadOnly]

    def __str__(self):
        return f"{self.enterprise.name} - {self.published}"


Enterprise.services = property(
    lambda self: self.extension.services if hasattr(self, "extension") else None
)
Enterprise.published = property(
    lambda self: self.extension.published if hasattr(self, "extension") else None
)
Enterprise.Meta.serializer_fields.append("services")
# Enterprise.Meta.nested_fields.append("services")
Enterprise.Meta.serializer_fields.append("published")
