import asyncio
from functools import wraps
from flask import Flask, request, render_template_string, jsonify, abort
from finalappRev1Search import mainFunctionForsearch
from flask_caching import Cache
from flask_limiter import Limiter
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import BadRequest
from flask_limiter.util import get_remote_address


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Set up caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


# limiter = Limiter(app, key_func=get_remote_address)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

API_KEY = '63bf1bb6967221fdecbcf27c712ff6d4'

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_method = request.headers.get('X-Auth-Method', 'API_KEY')

        if auth_method == 'API_KEY':
            api_key = request.headers.get('X-Api-Key')
            if api_key != API_KEY:
                abort(401, description="You are not authorized to access this API.")
        elif auth_method == 'OAUTH':
            # Implement OAuth 2.0 authentication here
            pass
        else:
            abort(400, description="Invalid authentication method.")

        return func(*args, **kwargs)

    return wrapper

def convert_sets_to_lists(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, list):
        return [convert_sets_to_lists(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_sets_to_lists(item) for item in obj)
    elif isinstance(obj, dict):
        return {k: convert_sets_to_lists(v) for k, v in obj.items()}
    else:
        return obj

@app.route('/keyword_search', methods=['GET', 'POST'])
@authenticate
@cache.cached(timeout=300)  # Cache results for 5 minutes
@limiter.limit("50 per day;5 per minute")  # Apply rate limiting
async def keyword_search():
    if request.method == "POST":
        words = request.form.get('words')
        if not words:
            raise BadRequest("Missing required parameter 'words'")

        result = mainFunctionForsearch(words)
        if not result:
            abort(404, description="No results found.")

        converted_result = convert_sets_to_lists(result)
        return jsonify(converted_result)
    else:
        return render_template_string('<form method="post">Words: <input type="text" name="words"><input type="submit"></form>')

if __name__ == '__main__':
    app.run(debug=True)
