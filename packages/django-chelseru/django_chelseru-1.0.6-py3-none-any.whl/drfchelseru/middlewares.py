from django.utils.timezone import datetime
from .models import Session
import user_agents

from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async


class TakeUserSessionMiddlaware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            ip = self.get_client_ip(request)

            if not request.session.session_key:
                request.session.create()
            
            session_key = request.session.session_key

            session, created = Session.objects.get_or_create(
                user = request.user,
                session_key = session_key,
                defaults = {
                    'user_agent': user_agent,
                    'ip_address': ip,
                    'device': user_agents.parse(user_agent).device.family,
                    'browser': user_agents.parse(user_agent).browser.family,
                }
            )

            session.user_agent = user_agent
            session.ip_address = ip
            session.last_seen = datetime.now()
            session.save()
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    


User = get_user_model()

@sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token["user_id"]
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token")
        
        if token:
            try:
                access_token = AccessToken(token[0])
                scope["user"] = await get_user(access_token)
            except Exception as e:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
