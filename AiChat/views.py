from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Chats, Messages
from .serializers import ChatsSerializer, MessagesSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .utils import chat_with_me

JWT_authenticator = JWTAuthentication()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createNewChat(request):
    try:
        user = request.user
        topic = request.data.get("topic", "Default Topic")

        new_chat = Chats.objects.create(user_id=user, topic=topic, room_name="dummy")
        serializer = ChatsSerializer(new_chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getMessages(request):
    messages = Messages.objects.order_by("-sent_at")[:3]
    serializer = MessagesSerializer(messages, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def getChatName(request):
    chat_id = request.data.get("chat_id")
    user_chat = Chats.objects.filter(chat_id=chat_id).first()
    serializer = ChatsSerializer(user_chat)
    return Response({"topic_name": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getAllMessages(request, chat_id):

    if chat_id is not None:
        messages = Messages.objects.filter(chat_id=chat_id).order_by("sent_at")
        serializer = MessagesSerializer(messages, many=True)
        return Response(serializer.data)
    else:
        return Response(
            {"error": "chat_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )


class UserChatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_chats = Chats.objects.filter(user_id=user)
        serializer = ChatsSerializer(user_chats, many=True)
        return Response(serializer.data)

    permission_classes = (IsAuthenticated,)

    def delete(self, request, chat_id):
        user = request.user
        user_chat = Chats.objects.filter(user_id=user, chat_id=chat_id).first()

        if user_chat:
            user_chat.delete()
            return Response(
                {"detail": "User chat deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"detail": "User chat not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, chat_id):
        response = JWT_authenticator.authenticate(request)
        patient, _ = response
        try:
            res = chat_with_me(request.data["ask"])

            data = {
                "chat_id": chat_id,
                "sender_id": patient.pk,
                "content": request.data["ask"],
                "response": res,
            }
            print(data)
            serializer = MessagesSerializer(data=data)

            if serializer.is_valid():
                msg = Messages(**serializer.validated_data)
                msg.save()

                return Response("Successfully Replied.", status=status.HTTP_200_OK)

            return Response("Unable to save Message", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"{e}", status=status.HTTP_400_BAD_REQUEST)


class RecentChatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            recent_chats = Chats.objects.order_by("-created_at")[:3]
            serializer = ChatsSerializer(recent_chats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
