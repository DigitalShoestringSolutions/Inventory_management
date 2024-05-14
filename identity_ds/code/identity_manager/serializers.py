from rest_framework import serializers

from .models import IdentityEntry, IdentityType

class IdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model=IdentityEntry
        fields = ('name',)
        depth=1

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        rep['id'] = obj.get_id()
        return rep

class IdentitySerializerFull(serializers.ModelSerializer):
    class Meta:
        model=IdentityEntry
        fields = ('name','description')
        depth=1

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        rep['id'] = obj.get_id()
        rep['individual'] = obj.type.individual
        return rep


class IdentityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=IdentityType
        fields=('tag','title','individual')
