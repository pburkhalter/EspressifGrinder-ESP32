import json
from lib.functools import wraps

from config import tokens
from lib.microdot import Response


def require_auth():
    def decorator(f):
        @wraps(f)
        def decorated_function(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization', None)

            if not auth_header:
                return Response("Authorization header is missing", status_code=401)

            try:
                token_type, token = auth_header.split()
                if not token_type.lower() == 'bearer':
                    return Response("Invalid token type", status_code=400)
                if not tokens.validate_token(token):
                    return Response("Invalid token, bye!", status_code=401)

            except ValueError:
                return Response("Invalid Authorization header format", status_code=400)

            return f(request, *args, **kwargs)

        return decorated_function

    return decorator


def require_content_type(required_content_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(request, *args, **kwargs):
            content_type = request.headers.get('Content-Type', '')

            if not content_type or content_type.split(';')[0] != required_content_type:
                return Response('Unsupported Media Type', status_code=415)

            return f(request, *args, **kwargs)

        return decorated_function

    return decorator
