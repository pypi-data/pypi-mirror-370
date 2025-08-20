import json

from django.db import IntegrityError
from djangoldp.activities import ActivityQueueService, as_activitystream
from djangoldp.activities.errors import (ActivityStreamDecodeError,
                                         ActivityStreamValidationError)
from djangoldp.models.models import invalidate_cache_if_has_entry
from djangoldp.views.commons import JSONLDRenderer
from djangoldp.views.ldp_api import LDPAPIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from djangoldp_becknld.activities import *
from djangoldp_becknld.models.transaction import Transaction


def get_transaction_from_activity(activity):
    transaction = None
    object = getattr(activity, "as:object", None)
    # TODO: Adapt me after stronger typing of as:object has been implemented
    transaction_id = object["beckn:transactionId"] if object else None
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except Transaction.DoesNotExist:
        pass

    return transaction


class BaseViewset(LDPAPIView):
    permission_classes = [
        AllowAny,
    ]
    renderer_classes = (JSONLDRenderer,)

    def post(self, request, *args, **kwargs):
        try:
            activity = json.loads(request.body, object_hook=as_activitystream)
            activity.validate()
        except ActivityStreamDecodeError:
            return Response(
                "Activity type unsupported", status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        except ActivityStreamValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        try:
            response = self._handle_activity(activity, **kwargs)
        except IntegrityError:
            return Response(
                "Unable to save due to an IntegrityError in the receiver model",
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        # always save activities
        obj = ActivityQueueService._save_sent_activity(
            activity.to_json(),
            local_id=request.build_absolute_uri(),
            success=True,
            type=activity.type,
        )

        if response:
            return response

        response = Response({}, status=status.HTTP_201_CREATED)
        response["Location"] = obj.urlid

        return response

    def _handle_activity(self, activity, **kwargs):
        pass
