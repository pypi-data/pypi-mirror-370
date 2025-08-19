from data_food_consortium.models import Enterprise
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import ReadOnly
from djangoldp_custom_dfc.models.__base import baseModel


class EnterpriseExtension(baseModel):
    enterprise = models.ForeignKey(
        Enterprise, on_delete=models.CASCADE, related_name="extension"
    )
    published = models.BooleanField(default=False)

    class Meta(baseModel.Meta):
        verbose_name = _("Publication Status")
        verbose_name_plural = _("Publication Status")

        rdf_type = "custom:Publication"
        permission_classes = [ReadOnly]
        disable_url = True

    def __str__(self):
        return f"{self.enterprise.name} - {self.published}"


@receiver(post_save, sender=Enterprise)
def create_enterprise_extension(sender, instance, created, **kwargs):
    if created or instance.extension is None:
        EnterpriseExtension.objects.create(enterprise=instance)
