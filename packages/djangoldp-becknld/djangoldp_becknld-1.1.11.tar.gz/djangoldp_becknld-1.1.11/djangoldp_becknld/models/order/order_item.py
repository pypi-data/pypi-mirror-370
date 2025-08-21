from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import InheritPermissions

from djangoldp_becknld.models.__base import baseModel
from djangoldp_becknld.models.order import Order
from djangoldp_becknld.models.order.quantitative_value import QuantitativeValue


class OrderItem(baseModel):
    order = models.ForeignKey(
        Order,
        related_name="ordered_items",
        on_delete=models.deletion.CASCADE,
    )
    item_offered = models.URLField()
    order_quantity = models.ForeignKey(
        QuantitativeValue, on_delete=models.deletion.CASCADE, null=True, blank=True
    )

    class Meta(baseModel.Meta):
        disable_url = True
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        permission_classes = [InheritPermissions]
        inherit_permissions = "order"
        rdf_type = "schema:OrderItem"

        serializer_fields = baseModel.Meta.serializer_fields + [
            "item_offered",
            "order_quantity",
        ]

        nested_fields = baseModel.Meta.nested_fields + ["order_quantity"]
