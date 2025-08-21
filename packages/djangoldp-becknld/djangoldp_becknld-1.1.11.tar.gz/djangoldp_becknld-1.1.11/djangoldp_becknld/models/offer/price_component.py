from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import InheritPermissions

from djangoldp_becknld.models.__base import baseNamedModel
from djangoldp_becknld.models.offer.price_specification import \
    PriceSpecification


class PriceComponent(baseNamedModel):
    price = models.FloatField()
    specification_offer = models.ForeignKey(
        PriceSpecification,
        on_delete=models.CASCADE,
        related_name="price_components",
        null=True,
        blank=True,
    )

    class Meta(baseNamedModel.Meta):
        disable_url = True
        verbose_name = _("Price Component")
        verbose_name_plural = _("Price Components")
        permission_classes = [InheritPermissions]
        inherit_permissions = "specification_offer"
        rdf_type = "schema:UnitPriceSpecification"

        serializer_fields = baseNamedModel.Meta.serializer_fields + [
            "price",
        ]
