from flask import Flask
from flask import render_template
import requests
import requests_cache
from penn import registrar
import json
import config

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

app = Flask(__name__)

requests_cache.install_cache('cache')
username = config.pit_username
password = config.pit_password
pcr_token = config.pcr_token


@app.route('/')
def index():
    return render_template('index.html')


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/pcr/<path:path>')
@crossdomain(origin='*')
def catchall(path):
    url = "http://api.penncoursereview.com/v1/"
    url += path
    url += pcr_token
    r = requests.get(url)
    return r.text


@app.route('/scheduler')
@crossdomain(origin='*')
def schedule():
    c = [x.strip() for x in request.args['class'].split('-')]
    reg = registrar.Registrar(username, password)
    section = reg.section(c[0], c[1], c[2])
    return json.dumps(section)


if __name__ == "__main__":
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()
