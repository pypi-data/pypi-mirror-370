from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import User as mobile, OTPCode, Session, MessageSMS, ChatRoom, MessageChat

# from django.contrib.auth import get_user_model

# UserGet = get_user_model()

class DefaultUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class MobileSerializer(ModelSerializer):
    class Meta:
        model = mobile
        fields = '__all__'
        depth = 1

class OTPCodeSerializer(ModelSerializer):
    class Meta:
        model = OTPCode
        fields = '__all__'
        read_only_fields = ('code', )


class SessionSerializer(ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class MessageSerializer(ModelSerializer):
    class Meta:
        model = MessageSMS
        fields = '__all__'


class ChatRoomSerializer(ModelSerializer):
    user_1, user_2 = DefaultUserSerializer(read_only=True), DefaultUserSerializer(read_only=True)
    class Meta:
        model = ChatRoom
        fields = '__all__'
        depth = 1


class MessageChatSerializer(ModelSerializer):
    sender = DefaultUserSerializer(read_only=True)
    
    class Meta:
        model = MessageChat
        fields = '__all__'
        depth = 1