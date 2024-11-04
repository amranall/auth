"""Python Flask WebApp Auth0 integration example
"""

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = "esdnkdjnsnsdnsdnnksdksdksdnksdnknksd"


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id="kmIgX3jZJ2RRNyWKhSCf8ZvYPf6ZSBbB",
    client_secret="oz-2QcRnIvhA6MAkrfJwxO5HAgyfPOSAjO0KKhmRI-1F4DoBabNB-S_6gG9Wbfgx",
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://dev-iqsxok7jiut551j0.us.auth0.com/.well-known/openid-configuration',
)


# Controllers API
@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://dev-iqsxok7jiut551j0.us.auth0.com"
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": "kmIgX3jZJ2RRNyWKhSCf8ZvYPf6ZSBbB",
            },
            quote_via=quote_plus,
        )
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
