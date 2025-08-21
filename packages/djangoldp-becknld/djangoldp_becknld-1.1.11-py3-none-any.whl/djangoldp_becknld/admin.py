from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin

from djangoldp_becknld.models import *


@admin.register(
    Address,
    DeliveryMethod,
    DeliveryOption,
    Invoice,
    Item,
    Offer,
    Order,
    OrderItem,
    PaymentOption,
    PriceComponent,
    PriceSpecification,
    QuantitativeValue,
)
class BecknldModelAdmin(DjangoLDPAdmin):
    readonly_fields = (
        "urlid",
        "creation_date",
        "update_date",
    )
    list_filter = (
        "creation_date",
        "update_date",
    )
    exclude = ("is_backlink", "allow_create_backlink")
    extra = 0


@admin.register(Transaction)
class TransactionAdmin(BecknldModelAdmin):
    readonly_fields = tuple(BecknldModelAdmin.readonly_fields) + ("transaction_id",)
