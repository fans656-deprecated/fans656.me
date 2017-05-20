import os

from flask import Flask, url_for, g, render_template

import views
import session

app = Flask(__name__)

app.route('/register', methods=['GET', 'POST'])(views.login.register)
app.route('/login', methods=['GET', 'POST'])(views.login.login)
app.route('/logout')(views.login.logout)

@app.route('/')
def index():
    return render_template('index.html', session=session.session_object())

@app.route('/user/<username>')
def user(username):
    s = session.session_object()
    s.visitor = username
    return render_template('user.html', session=s)

@app.teardown_appcontext
def close_db(err):
    if hasattr(g, 'db'):
        g.db.close()

@app.context_processor
def override_url_for():
    def f_(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(app.root_path,
                                         endpoint, filename)
                values['q'] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)
    return dict(url_for=f_)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
