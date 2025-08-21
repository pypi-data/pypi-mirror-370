from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import InheritPermissions

from djangoldp_becknld.models.__base import baseModel
from djangoldp_becknld.models.offer.delivery_method import DeliveryMethod
from djangoldp_becknld.models.offer.invoice import Invoice
from djangoldp_becknld.models.offer.price_specification import \
    PriceSpecification
from djangoldp_becknld.models.payment_option import PaymentOption

PAYMENT_STATUS = (
    ("schema:PaymentAutomaticallyApplied", _("PaymentAutomaticallyApplied")),
    ("schema:PaymentComplete", _("PaymentComplete")),
    ("schema:PaymentDeclined", _("PaymentDeclined")),
    ("schema:PaymentDue", _("PaymentDue")),
    ("schema:PaymentPastDue", _("PaymentPastDue")),
)

class Offer(baseModel):
    price_specification = models.OneToOneField(
        PriceSpecification,
        on_delete=models.CASCADE,
        related_name="offer",
    )
    delivery_method = models.OneToOneField(
        DeliveryMethod,
        related_name="offer",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    billing_address = models.OneToOneField(
        Invoice,
        related_name="offer",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=36, choices=PAYMENT_STATUS)

    @property
    def transaction_id(self):
        # "Offer.related_order" does reference the order that this offer is responding to
        return (
            self.related_order.transaction.transaction_id
            if self.related_order and self.related_order.transaction
            else None
        )

    class Meta(baseModel.Meta):
        disable_url = True
        verbose_name = _("Offer")
        verbose_name_plural = _("Offers")
        permission_classes = [InheritPermissions]
        rdf_type = "schema:Offer"

        serializer_fields = baseModel.Meta.serializer_fields + [
            "price_specification",
            "delivery_method",
            "billing_address",
            "payment_option",
            "payment_status",
        ]
        nested_fields = baseModel.Meta.nested_fields + [
            "price_specification",
            "delivery_method",
            "billing_address",
            "payment_option",
        ]
