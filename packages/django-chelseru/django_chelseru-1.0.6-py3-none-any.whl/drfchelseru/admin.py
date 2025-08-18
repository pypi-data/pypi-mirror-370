from django.contrib import admin
from .models import User, OTPCode, Session, MessageSMS, ChatRoom, MessageChat, ChatRoomPermissions, Organization


@admin.register(User)
class MobileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user__id', 'user__username', 'mobile', 'user__is_active']


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'mobile_number', 'created_at']
    ordering = ('-created_at', )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user__id', 'user__username', 'ip_address', 'last_seen']
    ordering = ('-created_at', )

@admin.register(MessageSMS)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'mobile_number', 'message_text', 'status']
    ordering = ('-created_at', )





admin.site.register(ChatRoom)
admin.site.register(MessageChat)
admin.site.register(ChatRoomPermissions)
admin.site.register(Organization)
