from django.test import TestCase
from .models import Conversation, Message

from .serializers import ChatRequestSerializer

from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status



class ConversationModelTests(TestCase):
    def test_conversation_created_with_timestamps(self):
        conversation = Conversation.objects.create()
        self.assertIsNotNone(conversation.created_at)
        self.assertIsNotNone(conversation.updated_at)

    def test_conversation_str(self):
        conversation = Conversation.objects.create()
        self.assertEqual(str(conversation), f"Conversation #{conversation.pk}")


class MessageModelTests(TestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create()

    def test_message_creation(self):
        message = Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.USER,
            content="Hello!",
        )
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello!")

    def test_messages_ordered_by_creation(self):
        first = Message.objects.create(
            conversation=self.conversation, role=Message.Role.USER, content="First"
        )
        second = Message.objects.create(
            conversation=self.conversation, role=Message.Role.ASSISTANT, content="Second"
        )
        messages = list(self.conversation.messages.all())
        self.assertEqual(messages, [first, second])

    def test_conversation_message_count(self):
        Message.objects.create(
            conversation=self.conversation, role=Message.Role.USER, content="Hi"
        )
        Message.objects.create(
            conversation=self.conversation, role=Message.Role.ASSISTANT, content="Hello!"
        )
        self.assertEqual(self.conversation.messages.count(), 2)



class ChatRequestSerializerTests(TestCase):
    def test_valid_message(self):
        serializer = ChatRequestSerializer(data={"message": "Hello"})
        self.assertTrue(serializer.is_valid())

    def test_blank_message_rejected(self):
        serializer = ChatRequestSerializer(data={"message": ""})
        self.assertFalse(serializer.is_valid())
        self.assertIn("message", serializer.errors)

    def test_whitespace_only_message_rejected(self):
        serializer = ChatRequestSerializer(data={"message": "   "})
        self.assertFalse(serializer.is_valid())

    def test_message_too_long_rejected(self):
        serializer = ChatRequestSerializer(data={"message": "a" * 2001})
        self.assertFalse(serializer.is_valid())

    def test_optional_conversation_id(self):
        serializer = ChatRequestSerializer(data={"message": "Hi", "conversation_id": 5})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["conversation_id"], 5)

    def test_conversation_id_not_required(self):
        serializer = ChatRequestSerializer(data={"message": "Hi"})
        self.assertTrue(serializer.is_valid())






class ChatAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/chat/"

    def test_empty_message_returns_400(self):
        response = self.client.post(self.url, {"message": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_message_field_returns_400(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("chatbot.views.get_bot_response")
    def test_valid_message_returns_200_and_answer(self, mock_get_bot_response):
        mock_get_bot_response.return_value = "This is a mocked answer."

        response = self.client.post(
            self.url, {"message": "What is your refund policy?"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["answer"], "This is a mocked answer.")
        self.assertIn("conversation_id", response.data)

    @patch("chatbot.views.get_bot_response")
    def test_messages_are_saved_to_database(self, mock_get_bot_response):
        mock_get_bot_response.return_value = "Mocked reply."

        response = self.client.post(
            self.url, {"message": "Hello there"}, format="json"
        )

        conversation_id = response.data["conversation_id"]
        conversation = Conversation.objects.get(id=conversation_id)
        self.assertEqual(conversation.messages.count(), 2)
        self.assertEqual(conversation.messages.first().content, "Hello there")
        self.assertEqual(conversation.messages.last().content, "Mocked reply.")

    @patch("chatbot.views.get_bot_response")
    def test_existing_conversation_id_reused(self, mock_get_bot_response):
        mock_get_bot_response.return_value = "Reply."
        existing = Conversation.objects.create()

        response = self.client.post(
            self.url,
            {"message": "Follow-up question", "conversation_id": existing.id},
            format="json",
        )

        self.assertEqual(response.data["conversation_id"], existing.id)

    @patch("chatbot.views.get_bot_response")
    def test_llm_service_error_returns_503(self, mock_get_bot_response):
        from .services.llm_service import LLMServiceError
        mock_get_bot_response.side_effect = LLMServiceError("API down")

        response = self.client.post(
            self.url, {"message": "Hello"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("error", response.data)