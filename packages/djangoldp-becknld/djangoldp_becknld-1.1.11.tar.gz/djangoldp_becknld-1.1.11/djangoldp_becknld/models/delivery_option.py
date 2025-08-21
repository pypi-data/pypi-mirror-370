from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import ReadOnly

from djangoldp_becknld.models.__base import baseNamedModel


class DeliveryOption(baseNamedModel):

    class Meta(baseNamedModel.Meta):
        disable_url = True
        verbose_name = _("Delivery Option")
        verbose_name_plural = _("Delivery Options")
        permission_classes = [ReadOnly]
        rdf_type = "schema:ParcelDelivery"
