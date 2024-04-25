from rest_framework import serializers
from .models import Oct


class OctSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oct
        fields = "__all__"
