from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import ReadOnly

from djangoldp_becknld.models.__base import baseNamedModel


class PaymentOption(baseNamedModel):

    class Meta(baseNamedModel.Meta):
        disable_url = True
        verbose_name = _("Payment Option")
        verbose_name_plural = _("Payment Options")
        permission_classes = [ReadOnly]
        rdf_type = "schema:PaymentMethod"
