import logging

from django.db import DatabaseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.shortcuts import render

from .models import Conversation, Message
from .serializers import ChatRequestSerializer, ChatResponseSerializer
from .services.chatbot_service import get_bot_response
from .services.llm_service import LLMServiceError
from .services.rag_service import RetrievalError
from .services.safety_service import looks_like_prompt_injection

logger = logging.getLogger(__name__)


class ChatView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid request.", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_message = serializer.validated_data["message"]
        conversation_id = serializer.validated_data.get("conversation_id")

        logger.info("Chat request received (conversation_id=%s)", conversation_id)

        if looks_like_prompt_injection(user_message):
            logger.warning("Possible prompt injection attempt: %s", user_message[:200])

        try:
            conversation = self._get_or_create_conversation(conversation_id)
        except DatabaseError:
            logger.exception("Database error while fetching/creating conversation")
            return Response(
                {"error": "The chatbot is temporarily unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            answer = get_bot_response(user_message, conversation=conversation)
        except RetrievalError:
            logger.exception("Knowledge base retrieval failed")
            return Response(
                {"error": "The chatbot's knowledge base is temporarily unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except LLMServiceError as e:
            logger.error("LLM service error: %s", e)
            return Response(
                {"error": "The chatbot is temporarily unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            logger.exception("Unexpected error generating bot response")
            return Response(
                {"error": "Something went wrong. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            Message.objects.create(
                conversation=conversation, role=Message.Role.USER, content=user_message,
            )
            Message.objects.create(
                conversation=conversation, role=Message.Role.ASSISTANT, content=answer,
            )
        except DatabaseError:
            logger.exception("Database error while saving messages")
            # The user still gets their answer even if saving history fails —
            # losing a history record is far less harmful than losing the answer.
            return Response(
                {"answer": answer, "conversation_id": conversation.id,
                 "warning": "Your message may not have been saved."},
                status=status.HTTP_200_OK,
            )
        logger.info("Chat response sent (conversation_id=%s)", conversation.id)

        response_data = {"answer": answer, "conversation_id": conversation.id}
        response_serializer = ChatResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def _get_or_create_conversation(self, conversation_id):
        if conversation_id:
            try:
                return Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                pass
        return Conversation.objects.create()


def chat_ui(request):
    return render(request, "chatbot/chat.html")