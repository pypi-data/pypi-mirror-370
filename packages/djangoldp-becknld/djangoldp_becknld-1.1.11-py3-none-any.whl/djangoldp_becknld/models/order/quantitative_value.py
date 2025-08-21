from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import InheritPermissions

from djangoldp_becknld.models.__base import baseModel


class QuantitativeValue(baseModel):
    value = models.FloatField()
    unit_text = models.CharField(max_length=254)

    class Meta(baseModel.Meta):
        disable_url = True
        verbose_name = _("Quantitative Value")
        verbose_name_plural = _("Quantitative Values")
        permission_classes = [InheritPermissions]
        inherit_permissions = "specification_offer"
        rdf_type = "schema:QuantitativeValue"

        serializer_fields = baseModel.Meta.serializer_fields + [
            "value",
            "unit_text",
        ]
