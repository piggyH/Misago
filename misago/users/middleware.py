from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser as DjAnonymousUser
from django.core.urlresolvers import resolve

from misago.users.bans import get_request_ip_ban, get_user_ban
from misago.users.models import AnonymousUser, Online
from misago.users.online import tracker


class RealIPMiddleware(object):
    def process_request(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            request._misago_real_ip = x_forwarded_for.split(',')[0]
        else:
            request._misago_real_ip = request.META.get('REMOTE_ADDR')


class AvatarServerMiddleware(object):
    def process_request(self, request):
        if request.path.startswith(settings.MISAGO_AVATAR_SERVER_PATH):
            request.user = DjAnonymousUser()
            resolved_path = resolve(request.path)
            return resolved_path.func(request, **resolved_path.kwargs)


class UserMiddleware(object):
    def process_request(self, request):
        if request.user.is_anonymous():
            request.user = AnonymousUser()
        elif not request.user.is_superuser:
            if get_request_ip_ban(request) or get_user_ban(request.user):
                logout(request)
        request.user.ip = request._misago_real_ip


class OnlineTrackerMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                request._misago_online_tracker = request.user.online_tracker
            except Online.DoesNotExist:
                tracker.start_tracking(request, request.user)
        else:
            request._misago_online_tracker = None

    def process_response(self, request, response):
        if hasattr(request, '_misago_online_tracker'):
            online_tracker = request._misago_online_tracker

            if online_tracker:
                if request.user.is_anonymous():
                    tracker.stop_tracking(request, online_tracker)
                else:
                    tracker.update_tracker(request, online_tracker)

        return response
