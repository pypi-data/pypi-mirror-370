from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import InheritPermissions

from djangoldp_becknld.models.__base import baseModel


class PriceSpecification(baseModel):
    price_currency = models.CharField(max_length=3)
    price = models.FloatField()

    class Meta(baseModel.Meta):
        disable_url = True
        verbose_name = _("Price Specification")
        verbose_name_plural = _("Price Specifications")
        permission_classes = [InheritPermissions]
        inherit_permissions = "offer"
        rdf_type = "schema:PriceSpecification"

        serializer_fields = baseModel.Meta.serializer_fields + [
            "price_currency",
            "price",
        ]
