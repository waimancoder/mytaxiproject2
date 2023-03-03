from rest_framework import serializers
from .models import Driver, Location, Block 

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['car_make', 'car_model', 'car_registration_number', 'driver_license_id', 'driver_license_img']

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('name', 'lat', 'lng')

class LocationSerializer(serializers.ModelSerializer):
    blocks = BlockSerializer(many=True)

    class Meta:
        model = Location
        fields = ('name', 'polygon', 'lat', 'lng', 'blocks')

    def update(self, instance, validated_data):
        blocks_data = validated_data.pop('blocks')
        blocks = instance.blocks.all()

        instance.name = validated_data.get('name', instance.name)
        instance.polygon = validated_data.get('polygon', instance.polygon)
        instance.lat = validated_data.get('lat', instance.lat)
        instance.lng = validated_data.get('lng', instance.lng)
        instance.save()

        for block_data in blocks_data:
            if blocks:
                block = blocks.pop(0)
                block.name = block_data.get('name', block.name)
                block.lat = block_data.get('lat', block.lat)
                block.lng = block_data.get('lng', block.lng)
                block.save()
            else:
                Block.objects.create(location=instance, **block_data)

        for block in blocks:
            block.delete()

        return instance