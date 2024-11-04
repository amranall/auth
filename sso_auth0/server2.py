import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = FastAPI()

# Add middleware for session management
app.add_middleware(SessionMiddleware, secret_key="esdnkdjnsnsdnsdnnksdksdksdnksdnknksd")

# Setup Jinja2 templates for rendering HTML
templates = Jinja2Templates(directory="templates")

# Auth0 configuration using Authlib
oauth = OAuth()
oauth.register(
    name="auth0",
    client_id="kmIgX3jZJ2RRNyWKhSCf8ZvYPf6ZSBbB",
    client_secret="oz-2QcRnIvhA6MAkrfJwxO5HAgyfPOSAjO0KKhmRI-1F4DoBabNB-S_6gG9Wbfgx",
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f"https://dev-iqsxok7jiut551j0.us.auth0.com/.well-known/openid-configuration",
)

# Home route
@app.get("/")
async def home(request: Request):
    user = request.session.get("user")
    pretty_user = json.dumps(user, indent=4) if user else None
    return templates.TemplateResponse("home2.html", {"request": request, "user": user, "pretty": pretty_user})

# Auth0 callback route
@app.get("/callback")
async def callback(request: Request):
    token = await oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return RedirectResponse(url="/")

# Login route
@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

# Logout route
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    home_url = str(request.base_url)
    logout_url = (
        "https://dev-iqsxok7jiut551j0.us.auth0.com/v2/logout?"
        + urlencode(
            {
                "returnTo": home_url,
                "client_id": "kmIgX3jZJ2RRNyWKhSCf8ZvYPf6ZSBbB",
            },
            quote_via=quote_plus,
        )
    )
    return RedirectResponse(url=logout_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(env.get("PORT", 3000)))
