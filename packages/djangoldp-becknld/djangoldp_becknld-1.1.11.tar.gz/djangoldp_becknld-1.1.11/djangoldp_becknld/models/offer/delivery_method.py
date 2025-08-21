from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import InheritPermissions

from djangoldp_becknld.models.__base import baseModel
from djangoldp_becknld.models.offer.address import Address


class DeliveryMethod(baseModel):
    delivery_address = models.ForeignKey(
        Address,
        related_name="delivery_method",
        on_delete=models.CASCADE,
    )
    contact_point = models.CharField(max_length=24)

    class Meta(baseModel.Meta):
        disable_url = True
        verbose_name = _("Delivery Method")
        verbose_name_plural = _("Delivery Methods")
        permission_classes = [InheritPermissions]
        inherit_permissions = "offer"
        serializer_fields = baseModel.Meta.serializer_fields + [
            "delivery_address",
            "contact_point",
        ]
        nested_fields = baseModel.Meta.nested_fields + ["delivery_address"]
        rdf_type = "schema:ParcelDelivery"
