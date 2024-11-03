from rest_framework import serializers
from .models import KeyValueStore

class KeyValueStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyValueStore
        fields = ['key', 'value']