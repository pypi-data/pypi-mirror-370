from django.db import models
from django.utils.translation import gettext_lazy as _

from djangoldp_becknld.models.__base import baseModel


# TODO: Temp model. Should be managed by the BPP itself
class Item(baseModel):
    item_id = models.URLField()
    unitary_price = models.FloatField()
    unit_text = models.CharField(max_length=254)

    class Meta(baseModel.Meta):
        disable_url = True
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        permission_classes = []
        rdf_type = "internal:Item"

        serializer_fields = baseModel.Meta.serializer_fields + [
            "item",
            "unitary_price",
            "unit_text",
        ]
