from data_food_consortium.models import Enterprise
from djangoldp.views.ldp_viewset import LDPViewSet


class EnterpriseViewset(LDPViewSet):
    model = Enterprise

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(extension__published=True)
