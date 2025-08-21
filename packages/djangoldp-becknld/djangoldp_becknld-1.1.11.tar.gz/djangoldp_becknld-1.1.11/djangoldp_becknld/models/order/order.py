from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import InheritPermissions

from djangoldp_becknld.models.__base import baseModel
from djangoldp_becknld.models.offer import Offer
from djangoldp_becknld.models.transaction import Transaction, tidgen


class Order(baseModel):
    transaction = models.ForeignKey(
        Transaction,
        related_name="orders",
        on_delete=models.deletion.CASCADE,
        null=True,
        blank=True,
    )
    responded_offer = models.OneToOneField(
        Offer,
        related_name="related_order",
        on_delete=models.deletion.CASCADE,
        null=True,
        blank=True,
    )
    order_number = models.CharField(max_length=36, default=tidgen)

    @property
    def transaction_id(self):
        return self.transaction.transaction_id if self.transaction else None

    class Meta(baseModel.Meta):
        disable_url = True
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        permission_classes = [InheritPermissions]
        inherit_permissions = "transaction"
        rdf_type = "schema:Order"

        serializer_fields = baseModel.Meta.serializer_fields + [
            "transaction_id",
            "order_number",
            "ordered_items",
        ]

        nested_fields = baseModel.Meta.nested_fields + ["ordered_items"]
