from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import InheritPermissions

from djangoldp_becknld.models.__base import baseNamedModel
from djangoldp_becknld.models.offer.address import Address


class Invoice(baseNamedModel):
    billing_address = models.ForeignKey(
        Address,
        related_name="invoice",
        on_delete=models.CASCADE,
    )
    email = models.EmailField()
    telephone = models.CharField(max_length=24)

    class Meta(baseNamedModel.Meta):
        disable_url = True
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        permission_classes = [InheritPermissions]
        inherit_permissions = "offer"
        serializer_fields = baseNamedModel.Meta.serializer_fields + [
            "billing_address",
            "email",
            "telephone",
        ]
        nested_fields = baseNamedModel.Meta.nested_fields + [
            "billing_address",
        ]
        rdf_type = "schema:Invoice"
