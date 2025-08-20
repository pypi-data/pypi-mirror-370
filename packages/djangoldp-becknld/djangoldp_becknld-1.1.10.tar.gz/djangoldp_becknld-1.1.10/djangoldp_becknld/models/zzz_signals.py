import requests
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from djangoldp.models.models import Activity

from djangoldp_becknld.consts import (BAP_URI, BECKNLD_CONTEXT, BPP_URI,
                                      IS_BAP, IS_BPP)
from djangoldp_becknld.models.transaction import Transaction


def _get_transaction_uri(server_uri, transaction_id=False):
    if not server_uri:
        return None

    if server_uri and server_uri[-1] != "/":
        server_uri += "/"

    if not transaction_id:
        return server_uri + "transactions/"

    return server_uri + "transactions/" + transaction_id + "/"


@receiver(post_save, sender=Transaction)
def handle_transaction_creation(sender, instance, created, **kwargs):
    if created:
        if IS_BAP:
            if not instance.bap_uri:
                # Reverse case only useful for gateways
                instance.bap_uri = instance.urlid
            if not instance.bpp_uri:
                instance.bpp_uri = _get_transaction_uri(
                    BPP_URI, instance.transaction_id
                )

        if IS_BPP:
            if not instance.bpp_uri:
                instance.bpp_uri = instance.urlid
            if not instance.bap_uri:
                instance.bpp_uri = _get_transaction_uri(
                    BAP_URI, instance.transaction_id
                )

        instance.save()

        if IS_BAP and not IS_BPP:
            res = requests.post(
                _get_transaction_uri(BPP_URI),
                json={
                    "@context": BECKNLD_CONTEXT,
                    "transaction_id": instance.transaction_id,
                    "bap_uri": instance.bap_uri,
                    "creator": {"@id": instance.creator.urlid},
                },
                headers={
                    "content-type": "application/ld+json",
                },
                timeout=5,
            )
            if res.status_code != 200:
                raise Exception


@receiver(post_delete, sender=Transaction)
def clear_related_activities_on_transaction_delete(sender, instance, **kwargs):
    if instance.urlid:
        Activity.objects.filter(
            Q(local_id=instance.bap_inbox)
            | Q(local_id=instance.bpp_inbox)
            | Q(local_id=instance.bap_outbox)
            | Q(local_id=instance.bpp_outbox)
        ).delete()
