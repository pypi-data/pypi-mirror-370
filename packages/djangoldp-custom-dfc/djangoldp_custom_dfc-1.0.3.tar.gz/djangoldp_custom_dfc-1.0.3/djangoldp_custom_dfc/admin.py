from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin

from djangoldp_custom_dfc.models import *


class BasicAdmin(DjangoLDPAdmin):
    exclude = ("is_backlink", "allow_create_backlink")
    extra = 0


class CustomDFCModelAdmin(BasicAdmin):
    readonly_fields = (
        "urlid",
        "creation_date",
        "update_date",
    )
    list_filter = (
        "creation_date",
        "update_date",
    )
    exclude = ("is_backlink", "allow_create_backlink")
    extra = 0


@admin.register(
    EnterpriseExtension,
)
class EnterpriseExtensionAdmin(CustomDFCModelAdmin):
    list_display = (
        "enterprise",
        "published",
        "creation_date",
        "update_date",
    )
    search_fields = [
        "enterprise__name",
    ]
    list_filter = tuple(CustomDFCModelAdmin.list_filter) + (
        "published",
    )
    ordering = ["enterprise"]
