from rest_framework import serializers
from .models import Conversation, Message


class ChatRequestSerializer(serializers.Serializer):
    """Validates the incoming request body for POST /api/chat/."""
    message = serializers.CharField(
        max_length=2000,
        allow_blank=False,
        trim_whitespace=True,
    )
    conversation_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]


class ChatResponseSerializer(serializers.Serializer):
    """Shapes the outgoing response body."""
    answer = serializers.CharField()
    conversation_id = serializers.IntegerField()