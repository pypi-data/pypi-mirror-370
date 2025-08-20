from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.permissions import ACLPermissions, AuthenticatedOnly, CreateOnly

from djangoldp_becknld.models.__base import baseModel


def tidgen():
    import uuid

    return str(uuid.uuid4())


class Transaction(baseModel):
    transaction_id = models.SlugField(max_length=36, default=tidgen)

    # When a transaction without a transaction_id is created, bap_uri is self.urlid
    # Else, it'll be provided by the BAP within the activity that'll create the mirror transaction in the BPP
    bap_uri = models.URLField(blank=True, null=True)

    # When a transaction with a transaction_id, bpp_uri is is self.urlid
    # Else it'll be populated after creating the mirror transaction in the BPP
    bpp_uri = models.URLField(blank=True, null=True)

    # Creator and initiators are only present in BAP
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_transactions",
        on_delete=models.deletion.CASCADE,
        null=True,
        blank=True,
    )

    initiators = models.OneToOneField(
        Group,
        related_name="transactions",
        on_delete=models.deletion.CASCADE,
        null=True,
        blank=True,
    )

    @property
    def bap_inbox(self):
        return (self.bap_uri + "inbox/") if self.bap_uri else None

    @property
    def bpp_inbox(self):
        return (self.bpp_uri + "inbox/") if self.bpp_uri else None

    @property
    def bap_outbox(self):
        return (self.bap_uri + "outbox/") if self.bap_uri else None

    @property
    def bpp_outbox(self):
        return (self.bpp_uri + "outbox/") if self.bpp_uri else None

    def __str__(self):
        return self.transaction_id or self.urlid

    class Meta(baseModel.Meta):
        # Optional as we don't serialize anything else, may be useful in the future
        depth = 4

        lookup_field = "transaction_id"
        ordering = ["transaction_id"]

        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

        serializer_fields = baseModel.Meta.serializer_fields + [
            "transaction_id",
            "bap_inbox",
            "bap_outbox",
            "bpp_uri",
            "bap_uri",
        ]

        auto_author = "creator"

        permission_roles = {
            "initiators": {
                "perms": ["view", "change", "control", "delete"],
                "add_author": True,
            },
        }

        permission_classes = [(AuthenticatedOnly & CreateOnly) | ACLPermissions]

        rdf_type = "becknld:Transaction"
