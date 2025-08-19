from django.urls import path

from djangoldp_custom_dfc.views import EnterpriseViewset

urlpatterns = (
    path(
        "enterprises/",
        EnterpriseViewset.urls(),
    ),
)
