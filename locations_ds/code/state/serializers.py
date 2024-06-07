from rest_framework import serializers

from .models import Edge, Event

class StateSerializer(serializers.ModelSerializer):
    child = serializers.StringRelatedField()
    parent = serializers.StringRelatedField()

    class Meta:
        model = Edge
        fields = ("edge_id","edge_type", "child", "parent", "start", "end", "quantity")

    # def to_representation(self, obj):
    # rep = super().to_representation(obj)
    # rep['location'] = rep['location']['name']
    # return rep


class EventSerializer(serializers.ModelSerializer):
    child = serializers.StringRelatedField()
    from_parent = serializers.StringRelatedField()
    to_parent = serializers.StringRelatedField()

    class Meta:
        model=Event
        fields = ('event_id','child','from_parent','to_parent',"timestamp","quantity")
