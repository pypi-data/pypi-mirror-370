from rest_framework import status
from rest_framework.response import Response

from djangoldp_becknld.consts import IS_BAP
from djangoldp_becknld.views.transaction.__base_viewset import BaseViewset
from djangoldp_becknld.views.transaction.outbox import *


class OutboxViewset(BaseViewset):
    def get(self, *args, **kwargs):
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def _handle_activity(self, activity, **kwargs):
        if not IS_BAP:
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        if activity.type == "confirm":
            return handle_confirm_activity(activity)
        elif activity.type == "init":
            return handle_init_activity(activity)
        elif activity.type == "select":
            return handle_select_activity(activity)
