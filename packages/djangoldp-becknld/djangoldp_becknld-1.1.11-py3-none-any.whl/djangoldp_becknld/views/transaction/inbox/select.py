from djangoldp.activities.services import ActivityQueueService
from rest_framework import status
from rest_framework.response import Response

from djangoldp_becknld.consts import BAP_URI, BECKNLD_CONTEXT, BPP_URI
from djangoldp_becknld.models.item import Item
from djangoldp_becknld.views.transaction.__base_viewset import \
    get_transaction_from_activity


def handle_select_activity(activity):
    transaction = get_transaction_from_activity(activity)

    if transaction:
        object = getattr(activity, "as:object", None)
        if object:
            ordereditem = object["schema:orderedItem"]
            if ordereditem:
                try:
                    new_activity = {
                        "@context": BECKNLD_CONTEXT,
                        "@type": ["as:Announce", "beckn:OnSelect"],
                        "type": "on_select",
                        "as:actor": {
                            "@id": transaction.bpp_outbox,
                            "schema:name": BPP_URI,  # TODO: Where to find self name?
                        },
                        "as:target": {
                            "@id": transaction.bap_inbox,
                            "schema:name": BAP_URI,
                        },
                        "as:object": {
                            "@type": "schema:Order",
                            "beckn:transactionId": transaction.transaction_id,
                            "schema:orderedItem": ordereditem,
                            "schema:acceptedOffer": {
                                "@type": "schema:Offer",
                                "schema:priceSpecification": {
                                    "@type": "schema:PriceSpecification",
                                    "schema:priceCurrency": "INR",  # TODO: Hard-coded for demonstration purpose
                                    "schema:price": "0",
                                    "schema:priceComponent": [],
                                },
                            },
                            "schema:potentialAction": {  # TODO: Hard-coded for demonstration purpose
                                "@type": "schema:ParcelDelivery",
                                "schema:deliveryAddress": {
                                    "schema:postalCode": "560001",
                                    "schema:addressCountry": "IN"
                                },
                                "geo:lat": 12.9716,
                                "geo:long": 77.5946
                            },
                        },
                        "beckn:context": {
                            "beckn:domain": "retail",  # TODO: Hard-coded for demonstration purpose
                            "schema:country": "IND",  # TODO: Hard-coded for demonstration purpose
                            "schema:city": "std:080",  # TODO: Hard-coded for demonstration purpose
                            "beckn:coreVersion": "1.1.0",  # TODO: Hard-coded for demonstration purpose
                            "dc:created": str(transaction.update_date),
                        },
                    }

                    # TODO: Don't do that on the fly.
                    # TODO: Generate a real order/offer combination, save them in bpp db

                    new_activity["as:object"]["schema:orderNumber"] = "123"  # TODO: Retrieve from DB

                    total_price = 0
                    for item in ordereditem:
                        item_offered = item["schema:itemOffered"]
                        item_id = item_offered["@id"] if item_offered else None
                        if item_id:
                            quantity = item["schema:orderQuantity"]
                            if quantity:
                                quantity_value = quantity["schema:value"]
                                if quantity["schema:unitText"]:
                                    quantity_unit = quantity["schema:unitText"]

                            try:
                                if quantity_unit:
                                    item_ref = Item.objects.get(
                                        item_id=item_id,
                                        unit_text=quantity_unit,
                                    )
                                else:
                                    item_ref = Item.objects.get(item_id=item_id)
                            except Item.DoesNotExist:
                                pass

                            if item_ref:

                                price = item_ref.unitary_price

                                if quantity_value:
                                    price *= quantity_value

                                new_activity["as:object"]["schema:acceptedOffer"][
                                    "schema:priceSpecification"
                                ]["schema:priceComponent"].append(
                                    {
                                        "@type": "schema:UnitPriceSpecification",
                                        "schema:itemOffered": item_ref.item_id,
                                        "schema:price": str(price),
                                    }
                                )

                                total_price += price
                            else:
                                # TODO: Log this exception
                                return Response(
                                    "Item not found",
                                    status=status.HTTP_404_NOT_FOUND,
                                )

                        else:
                            # TODO: Log this exception
                            return Response(
                                "Item missing @id",
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                    new_activity["as:object"]["schema:acceptedOffer"][
                        "schema:priceSpecification"
                    ]["price"] = total_price

                    ActivityQueueService.send_activity(
                        transaction.bap_inbox, new_activity
                    )
                    return Response(new_activity, status=status.HTTP_201_CREATED)
                except Exception:
                    # TODO: Log this exception
                    return Response(
                        "Unable to parse activity",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                "Missing schema:orderedItem", status=status.HTTP_400_BAD_REQUEST
            )
        return Response("Missing as:object", status=status.HTTP_400_BAD_REQUEST)

    return Response("Transaction not found", status=status.HTTP_404_NOT_FOUND)
