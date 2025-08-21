import json

from django.http import Http404
from djangoldp.models import Activity
from rest_framework import status
from rest_framework.response import Response

from djangoldp_becknld.consts import BECKNLD_CONTEXT, IS_BAP
from djangoldp_becknld.models.transaction import Transaction
from djangoldp_becknld.views.transaction.__base_viewset import BaseViewset


# TODO: Permissions based on User x Transaction
class InboxActivityViewset(BaseViewset):
    def get(self, request, transaction_id, activity_id, *args, **kwargs):
        if not IS_BAP:
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            if transaction and transaction.urlid:
                activity = Activity.objects.get(id=activity_id)
                serializable_payload = json.loads(activity.payload)
                serializable_payload["@id"] = request.build_absolute_uri()
                serializable_payload["@context"] = BECKNLD_CONTEXT
                # Response is cacheable, as activity should not change
                return Response(
                    serializable_payload,
                    headers={
                        "content-type": "application/ld+json",
                        "Access-Control-Allow-Origin": "*",
                        "Cache-Control": "public, max-age=3600",
                    },
                )
        except Transaction.DoesNotExist or Activity.DoesNotExist:
            pass

        raise Http404
