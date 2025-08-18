# simulator/serializers.py


from rest_framework import serializers
from .models import SimulationRun, SimulatorLog


class SimulationRunSerializer(serializers.ModelSerializer):
    api_key_prefix = serializers.SerializerMethodField()

    class Meta:
        model = SimulationRun
        fields = ['id', 'user', 'api_key_prefix', 'status', 'started_at', 'ended_at', 'alignment_score']

    def get_api_key_prefix(self, obj):
        return obj.api_key.prefix if obj.api_key else None

class SimulatorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulatorLog
        fields = [
            'id', 'run', 'timestamp', 'response',
            'alignment_score', 'color', 'flatline', 'violations', 'confidence', 'prompt'
        ]

