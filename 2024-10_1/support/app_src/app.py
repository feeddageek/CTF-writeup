from flask import Flask, redirect, session, request, render_template
import uuid
import utils
import users
from errors import ApplicationException
import requests
import urllib
import secrets
import os


app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

PAGE_INDEX = "/index.html"
PAGE_404 = "/404.html"
PAGE_LOGIN = "/login.html"
PAGE_LOGOUT = "/logout.html"
PAGE_USER = "/user.html"
PAGE_GET_USER = "/profile.html"
PAGE_SUPERADMIN = "/superadmin.html"

rbac = {
    "/": ["guest", "user"],
    PAGE_INDEX: ["guest", "user"],
    PAGE_404: ["guest", "user"],
    PAGE_LOGIN: ["guest", "user"],
    PAGE_LOGOUT: ["user"],
    PAGE_USER: ["user"],
    PAGE_GET_USER: ["user"],
    PAGE_SUPERADMIN: ["admin"],
}


@app.before_request
def session_middleware():
    if "roles" not in session or session["roles"] == None:
        session["roles"] = ["guest"]


@app.before_request
def rbac_middleware():
    if request.path.startswith('/static/'):
        return

    page = utils.get_request_page(request)

    if page in rbac.keys():
        has_role = False

        for role in rbac[page]:
            if role in session["roles"]:
                has_role = True
                break

        if not has_role:
            return redirect("/login.html")
    else:
        return redirect("/404.html")


@app.before_request
def superadmin_middleware():
    if request.path == "/superadmin.html":
        if "roles" not in session["roles"] and "admin" not in session["roles"]:
            session.clear()
            return redirect("login.html")


@app.context_processor
def inject_data() -> dict:
    return {'username': session['username'] if "username" in session else "", 'isAdmin': 'admin' in session['roles']}


@app.route("/", methods=["GET"])
def indexDefault():
    return redirect("/index.html")


@app.route(PAGE_INDEX, methods=["GET"])
def index():
    return render_template('index.html')


@app.route(PAGE_LOGIN, methods=["GET"])
def login():
    if "username" in session and session["username"] != None:
        return redirect(PAGE_USER)
    return render_template('login.html')


@app.route(PAGE_LOGIN, methods=["POST"])
def authenticate():
    res = requests.post("http://127.0.0.1:4000/auth", {'username': request.form.get(
        "username"), 'password': request.form.get('password')})

    if (res.status_code == 200):
        result = res.json()
        session.update({
            'username': result['username'],
            'roles': result['roles']
        })

        return redirect(PAGE_USER)

    return render_template('login.html', error="Invalid credentials")


@app.route(PAGE_LOGOUT, methods=["GET"])
def logout():
    session.clear()
    return redirect(PAGE_INDEX)


@app.route(PAGE_USER, methods=["GET"])
def user():
    return render_template('user.html', username=session["username"] if "username" in session else "", roles=session["roles"])


@app.route(PAGE_GET_USER, methods=["GET"])
def getUserProfile():
    if (request.args.get('user') == None):
        return redirect(PAGE_USER)

    result = users.getByUsername(request.args.get('user'))
    return render_template('profile.html', username=result["username"], roles=result["roles"])


@app.route(PAGE_SUPERADMIN, methods=["GET"])
def admin():
    return render_template('admin.html')


@app.route(PAGE_SUPERADMIN, methods=["POST"])
def checkurl():
    url = request.form.get('url')

    (scheme, host, path, query, fragment) = urllib.parse.urlsplit(url)

    if host == "127.0.0.1:4000":
        requestUrl = urllib.parse.urlunsplit(
            ('http', '127.0.0.1:4000', path, query, fragment))
    else:
        # Preventing calls to another host
        requestUrl = urllib.parse.urlunsplit(('', '', path, query, fragment))
    try:
        res = requests.get(requestUrl)
    except:
        class MockResponse:
            def __init__(self):
                self.status_code = 400
        res = MockResponse()

    if (res.status_code == 200):
        return render_template('admin.html', result=res.text)
    else:
        return render_template('admin.html', error="Unable to get URL")


@app.route(PAGE_404, methods=["GET"])
def notFound():
    return render_template("404.html")


@app.errorhandler(404)
def pageNotFound(e):
    return redirect("/404.html")


@app.errorhandler(ApplicationException)
def handle_bad_request(e):
    message = (str(e).format(error=e))
    print(message)
    return render_template("error.html", message=message), 400


app.run(host="0.0.0.0", port=3000)
