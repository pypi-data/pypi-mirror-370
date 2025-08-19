from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import Model
from djangoldp.permissions import AnonymousReadOnly, ReadAndCreate


class baseModel(Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.urlid

    class Meta(Model.Meta):
        abstract = True
        verbose_name = _("Unknown Object")
        verbose_name_plural = _("Unknown Objects")

        serializer_fields = [
            "@id",
            "creation_date",
            "update_date",
        ]
        nested_fields = []
        rdf_type = "sib:BasicObject"
        permission_classes = [AnonymousReadOnly, ReadAndCreate]


class baseNamedModel(baseModel):
    name = models.CharField(max_length=254, blank=True, null=True, default="")

    def __str__(self):
        return self.name or self.urlid

    class Meta(baseModel.Meta):
        abstract = True
        serializer_fields = [
            "@id",
            "creation_date",
            "update_date",
            "name",
        ]
