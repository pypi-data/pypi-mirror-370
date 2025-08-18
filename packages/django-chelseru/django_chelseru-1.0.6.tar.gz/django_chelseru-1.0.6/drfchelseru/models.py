from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as default_user
from django.utils.timezone import now, timedelta
from random import randint
from .settings import auth_init_check

UserGet = get_user_model()

class User(models.Model):
    user = models.OneToOneField(default_user, on_delete=models.CASCADE, related_name='mobile_drf_chelseru')
    mobile = models.CharField(max_length=11)
    group = models.IntegerField(default=0, help_text='choice group type or user level, with numbers.')

    def __str__(self):
        return f'{self.user.username} | {self.mobile}'


class OTPCode(models.Model):
    code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.code} -> {self.mobile_number} | {self.created_at}'

    def save(self, *args, **kwargs):
        """
        Generates a new random code if one does not already exist.
        """
        if not self.code:
            icheck = auth_init_check()
            if icheck and isinstance(icheck, dict):
                otp_len = icheck['OPTIONS']['len']
                otp_exp_time = icheck['OPTIONS']['exp_time']

                self.code = str(randint(int('1' + (otp_len - 1) * '0'), int(otp_len * '9')))
        super().save(*args, **kwargs)

    def check_code(self):
        try:
            icheck = auth_init_check()
            if icheck and isinstance(icheck, dict):
                otp_exp_time = icheck['OPTIONS']['exp_time']
                if now().timestamp() <= (self.created_at + timedelta(seconds=otp_exp_time * 60)).timestamp():
                    self.delete()
                    return True
                self.delete()
        except:
            pass
        return False


class Session(models.Model):
    user = models.ForeignKey(default_user, models.DO_NOTHING, related_name='session_drf_chelseru')
    session_key = models.CharField(max_length=40, unique=True)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    device = models.TextField()
    browser = models.TextField()

    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'{self.user} - {self.ip_address}'


class MessageSMS(models.Model):
    message_text = models.TextField()
    mobile_number = models.CharField(max_length=20)
    _from = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'to: {self.mobile_number} , at: {self.created_at}'
    

class Organization(models.Model):
    owner = models.OneToOneField(UserGet, related_name='organization_drf_chelseru', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=45)
    uname = models.CharField(max_length=45, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'owner: {self.owner} - unique name: {self.uname}'


class ChatRoomPermissions(models.Model):
    READ_ONLY = 0
    MEMBER = 1
    CAN_ADD_MEMBER = 2
    CAN_KICK_MEMBER = 3
    CAN_BAN_MEMBER = 4
    CAN_ADD_ACCESS = 5
    CAN_REMOVE_ACCESS = 6
    CAN_KICK_ADMIN = 7
    CAN_CLOSE_CHAT = 8
    CAN_REOPEN_CHAT = 9
    CAN_RENAME_CHAT = 10
    CAN_UPDATE_AVATAR = 11
    CAN_DELETE_CHAT = 12

    ACCESS_CHOICES = [
        (READ_ONLY, 'Read Only'),
        (MEMBER, 'Member'),
        (CAN_ADD_MEMBER, 'Can Add Members'),
        (CAN_KICK_MEMBER, 'Can Kick Members'),
        (CAN_BAN_MEMBER, 'Can Ban Members'),
        (CAN_ADD_ACCESS, 'Can Add Access'),
        (CAN_REMOVE_ACCESS, 'Can Remove Accessa'),
        (CAN_KICK_ADMIN, 'Can Kick Admins'),
        (CAN_CLOSE_CHAT, 'Can Close Chat Room'),
        (CAN_REOPEN_CHAT, 'Can ReOpen Chat Room'),
        (CAN_RENAME_CHAT, 'Can Rename Chat Room'),
        (CAN_UPDATE_AVATAR, 'Can Update Chatroom Avatar'),
        (CAN_DELETE_CHAT, 'Can Delete Chat Room'),
    ]
    user = models.ManyToManyField(UserGet, related_name='user_drf_chelseru')
    access = models.IntegerField(choices=ACCESS_CHOICES, default=MEMBER)

    def __str__(self):
        return f'user: {self.user} - access: {self.access}'


class ChatRoom(models.Model):
    STATUS_OPEN = 1
    STATUS_CLOSE = 2
    STATUS_HOLD = 3

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSE, 'Close'),
        (STATUS_HOLD, 'Hold')
    ]

    user_1 = models.ForeignKey(UserGet, on_delete=models.CASCADE, related_name='user1_chats_drf_chelseru', blank=True, null=True)
    user_2 = models.ForeignKey(UserGet, on_delete=models.CASCADE, related_name='user2_chats_drf_chelseru', blank=True, null=True)

    users = models.ManyToManyField(UserGet, blank=True, related_name='users_drf_chelseru')
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, related_name='chatroom_drf_chelseru', blank=True, null=True)
    pinned_for = models.ManyToManyField(UserGet, blank=True, related_name='pinned_drf_chelseru')
    permissions = models.ManyToManyField(ChatRoomPermissions, blank=True, related_name='permissions_drf_chelseru')
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_OPEN)
    banneds = models.ManyToManyField(UserGet, blank=True, related_name='bans_drf_chelseru')
    name = models.CharField(max_length=45, blank=True, null=True)
    descriptions = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ID: {self.id}"


class MessageChat(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages_chat_drf_chelseru')
    sender = models.ForeignKey(UserGet, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"iD: {self.id} | Message from {self.sender.username} at {self.timestamp} | Chatroom ID: {self.chat_room.id}"