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
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from user_account.models import User
import json
from channels.layers import get_channel_layer
import redis
from django.conf import settings
from asgiref.sync import sync_to_async


channel_layer = get_channel_layer()

class DriverConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Extract the user ID from the WebSocket URL
        user_id = self.scope['url_route']['kwargs']['user_id']

        # Check if the user ID is valid (e.g. exists in the database)
        try:
            user = await sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            await self.close()
            return

        # Add the user ID to the channel group for drivers
        await self.channel_layer.group_add(
            'drivers', self.channel_name
        )
       
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user ID from the channel group for drivers
        print('Removing')
        await self.channel_layer.group_discard('drivers', self.channel_name)

    async def receive(self, text_data):
        # Parse the incoming JSON message
        data = json.loads(text_data)

        # Extract the message content
        message = data['message']

        response = {
            'status': 'success',
            'message': f"Received message: {message}"
        }
        await self.send(json.dumps(response))

        # Broadcast the message to all drivers
        await self.channel_layer.group_send(
            'drivers',
            {
                'type': 'driver_message',
                'message': message
            }
        )

    async def driver_message(self, event):
        # Send a message to the client
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
