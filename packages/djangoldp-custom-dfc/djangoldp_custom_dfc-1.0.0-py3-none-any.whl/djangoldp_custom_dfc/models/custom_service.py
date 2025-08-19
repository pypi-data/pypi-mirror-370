from django.utils.translation import gettext_lazy as _

from djangoldp_custom_dfc.models.__base import baseNamedModel


class Service(baseNamedModel):

    class Meta(baseNamedModel.Meta):
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

        serializer_fields = baseNamedModel.Meta.serializer_fields
        rdf_type = "custom:Service"
