from rest_framework import serializers
from .models import MAMMO


class MAMMOSerializer(serializers.ModelSerializer):
    class Meta:
        model = MAMMO
        fields = "__all__"
