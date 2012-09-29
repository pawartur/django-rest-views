import json
import base64
from functools import wraps
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden 
from django.contrib.auth import authenticate, login

def login_required_ajax(view_func=None, login_url=None, enable_basic_auth=None):
    enable_basic_auth = True if enable_basic_auth is None else enable_basic_auth
    def decorator(view_func):
        @wraps(view_func)
        def view(request, *args, **kwargs):
            auth = request.META.get('HTTP_AUTHORIZATION', '').split()

            if enable_basic_auth and len(auth) == 2 and auth[0].lower() == "basic":
                username, password = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=username, password=password)
                if user and user.is_active:
                    request.user = user

            if request.user.is_authenticated():
                return view_func(request, *args, **kwargs)

            if request.is_ajax():
                content = {
                    "message": "Login required",
                    "login_url": login_url or settings.LOGIN_URL
                }
                return HttpResponse(content=json.dumps(content), mimetype="application/json")
            elif enable_basic_auth:
                response = HttpResponse()
                response.status_code = 401
                response['WWW-Authenticate'] = 'Basic realm=""'
                return response
            else:
                # This is a fallback for cases when this decorator
                # is used for views that are not called with AJAX nor
                # are they authenticated by basic auth.
                return HttpResponseForbidden()

        return view
    if view_func is None:
        return decorator
    return decorator(view_func)
