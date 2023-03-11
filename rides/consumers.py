from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from channels.db import database_sync_to_async
from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import get_object_or_404
from rides.models import DriverLocation
from rides.serializers import DriverLocationSerializer
from typing import List
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.mixins import RetrieveModelMixin


class DriverLocationsConsumer(GenericAsyncAPIConsumer):
    queryset = DriverLocation.objects.all()
    serializer_class = DriverLocationSerializer
    permission_classes = [permissions.AllowAny]
    lookup_fields = 'user_id'
    lookup_url_kwarg = 'user_id'

    def get_object(self, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        user_id = kwargs['user_id']
        obj = get_object_or_404(queryset, user_id=user_id)
        return obj
    
    @action()
    async def get_driver_location(self, user_id, **kwargs):
        """
        Retrieve a single DriverLocation instance by driver ID and return it as a response.
        """
        try:
            driver_location = await database_sync_to_async(self.get_object)(user_id=user_id)
            print(driver_location.latitude)
        except ObjectDoesNotExist:
            raise ValueError('Driver location not found.')
        
        if driver_location.latitude is None or driver_location.longitude is None:
            return await self.reply(
                action='get_driver_location',
                status='Driver location found but latitude and/or longitude are NULL.',
            )

        latitude = float(driver_location.latitude)
        longitude = float(driver_location.longitude)
        data = {
            "latitude": latitude,
            "longitude": longitude
        }
        await self.reply(
            action='get_driver_location',
            status= "Driver location found",
            data = data
        )
    


