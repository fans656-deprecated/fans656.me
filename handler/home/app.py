from flask import *

from handler import handle


app = Flask(__name__)


@app.route('/')
def index():
    return handle(request=request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, threaded=True, debug=True)
