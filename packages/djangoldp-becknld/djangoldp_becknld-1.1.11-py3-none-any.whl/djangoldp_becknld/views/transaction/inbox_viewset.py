import json

from django.http import Http404
from djangoldp.models import Activity
from rest_framework import status
from rest_framework.response import Response

from djangoldp_becknld.consts import BECKNLD_CONTEXT, IS_BAP, IS_BPP
from djangoldp_becknld.models.transaction import Transaction
from djangoldp_becknld.views.transaction.__base_viewset import BaseViewset
from djangoldp_becknld.views.transaction.inbox import *


class InboxViewset(BaseViewset):
    def get(self, request, transaction_id, *args, **kwargs):
        if not IS_BAP:
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        # TODO: Permissions based on VC
        response = {
            "@context": BECKNLD_CONTEXT,
            "@id": request.build_absolute_uri(),
            "@type": "ldp:Container",
            "ldp:contains": [],
        }
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            if transaction and transaction.urlid:
                related_activities = Activity.objects.filter(
                    local_id=(transaction.urlid + "inbox/")
                ).order_by("-created_at")
                # Should we return only the last one?

                if related_activities:
                    for activity in related_activities:
                        serializable_payload = json.loads(activity.payload)
                        serializable_payload["@id"] = (
                            activity.local_id + str(activity.id) + "/"
                        )
                        response["ldp:contains"].append(serializable_payload)

                # Response is not cacheable, must revalidate
                response = Response(
                    response,
                    headers={
                        "content-type": "application/ld+json",
                        "Access-Control-Allow-Origin": "*",
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                    },
                )
                return response
        except Transaction.DoesNotExist:
            pass

        raise Http404

    def _handle_activity(self, activity, **kwargs):
        if activity.type == "confirm" and (IS_BAP or IS_BPP):
            return handle_confirm_activity(activity)
        elif activity.type == "init" and (IS_BAP or IS_BPP):
            return handle_init_activity(activity)
        elif activity.type == "select" and (IS_BAP or IS_BPP):
            return handle_select_activity(activity)
        elif activity.type == "on_confirm" and IS_BAP:
            return handle_on_confirm_activity(activity)
        elif activity.type == "on_init" and IS_BAP:
            return handle_on_init_activity(activity)
        elif activity.type == "on_select" and IS_BAP:
            return handle_on_select_activity(activity)
        return Response({}, status=status.HTTP_403_FORBIDDEN)
