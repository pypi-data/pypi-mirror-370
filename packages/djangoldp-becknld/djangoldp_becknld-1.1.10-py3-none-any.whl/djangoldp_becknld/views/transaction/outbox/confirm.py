from djangoldp.activities.services import ActivityQueueService
from rest_framework import status
from rest_framework.response import Response

from djangoldp_becknld.consts import BAP_URI, BECKNLD_CONTEXT, BPP_URI
from djangoldp_becknld.views.transaction.__base_viewset import \
    get_transaction_from_activity


def handle_confirm_activity(activity):
    transaction = get_transaction_from_activity(activity)

    if transaction:
        object = getattr(activity, "as:object", None)
        if object:
            orderNumber = object["schema:orderNumber"]
            if orderNumber:
                try:
                    new_activity = {
                        "@context": BECKNLD_CONTEXT,
                        "@type": ["as:Announce", "beckn:Confirm"],
                        "type": "confirm",
                        "as:actor": {
                            "@id": transaction.bap_outbox,
                            "schema:name": BAP_URI,  # TODO: Where to find self name?
                        },
                        "as:target": {
                            "@id": transaction.bpp_inbox,
                            "schema:name": BPP_URI,
                        },
                        "as:object": {
                            "@type": "schema:Order",
                            "beckn:transactionId": transaction.transaction_id,
                            "schema:orderNumber": orderNumber,
                        },
                        "beckn:context": {
                            "beckn:domain": "retail",  # TODO: Hard-coded for demonstration purpose
                            "schema:country": "IND",  # TODO: Hard-coded for demonstration purpose
                            "schema:city": "std:080",  # TODO: Hard-coded for demonstration purpose
                            "beckn:coreVersion": "1.1.0",  # TODO: Hard-coded for demonstration purpose
                            "dc:created": str(transaction.update_date),
                        },
                    }

                    if object["schema:paymentMethod"]:
                        # TODO: Validate this object
                        new_activity["as:object"]["schema:paymentMethod"] = object[
                            "schema:paymentMethod"
                        ]

                    if object["schema:deliveryMethod"]:
                        # TODO: Validate this value
                        new_activity["as:object"]["schema:deliveryMethod"] = object[
                            "schema:deliveryMethod"
                        ]

                    ActivityQueueService.send_activity(
                        transaction.bpp_inbox, new_activity
                    )

                    return Response(new_activity, status=status.HTTP_201_CREATED)

                except Exception:
                    # TODO: Log this exception
                    return Response(
                        "Unable to forward activity",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                "Missing schema:orderNumber", status=status.HTTP_400_BAD_REQUEST
            )

        return Response("Missing as:object", status=status.HTTP_400_BAD_REQUEST)

    return Response("Transaction not found", status=status.HTTP_404_NOT_FOUND)
