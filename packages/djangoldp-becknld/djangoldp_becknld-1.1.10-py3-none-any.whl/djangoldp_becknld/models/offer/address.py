from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import InheritPermissions

from djangoldp_becknld.models.__base import baseNamedModel


class Address(baseNamedModel):
    steet_address = models.CharField(max_length=254)
    address_locality = models.CharField(max_length=254)
    address_region = models.CharField(max_length=254)
    address_country = models.CharField(max_length=254)
    postal_code = models.CharField(max_length=254)

    class Meta(baseNamedModel.Meta):
        disable_url = True
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        permission_classes = [InheritPermissions]
        inherit_permissions = ["delivery_method", "invoice"]
        serializer_fields = baseNamedModel.Meta.serializer_fields + [
            "steet_address",
            "address_locality",
            "address_region",
            "address_country",
            "postal_code",
        ]
        rdf_type = "schema:deliveryAddress"
