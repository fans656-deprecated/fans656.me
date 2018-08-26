
import flask
from flask_cors import CORS

import file_util
import conf
from endpoints import endpoints
import util
from util import success_response, error_response

app = flask.Flask(__name__, static_folder='')
CORS(app)

for method, path, viewfunc in endpoints:
    viewfunc = util.handle_exceptions(viewfunc)
    app.route(path, methods=[method])(viewfunc)


@app.route('/')
def index():
    return 'hello'


@app.after_request
def after_request(response):
    if 'Access-Control-Allow-Origin' not in response.headers:
        response.headers.add('Access-Control-Allow-Origin',
                             flask.request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


if __name__ == '__main__':
    print 'hi'
    app.run(debug=True, host='0.0.0.0', port=4430, threaded=True)
