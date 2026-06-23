from rest_framework import serializers


class URLAnalysisInputSerializer(serializers.Serializer):
    url = serializers.CharField(min_length=4, max_length=2048, trim_whitespace=True)


class SMSAnalysisInputSerializer(serializers.Serializer):
    text = serializers.CharField(min_length=3, max_length=5000, trim_whitespace=True)


class AnalysisResultSerializer(serializers.Serializer):
    analysis_id = serializers.UUIDField()
    verdict = serializers.ChoiceField(choices=("safe", "suspicious", "dangerous"))
    risk_score = serializers.IntegerField(min_value=0, max_value=100)
    reasons = serializers.ListField(child=serializers.CharField())
    signals = serializers.ListField(child=serializers.CharField())
    privacy = serializers.CharField()

