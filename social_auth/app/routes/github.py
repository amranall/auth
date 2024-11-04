from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from oauthlib.oauth2 import WebApplicationClient
import requests
import uuid
import os


router = APIRouter()

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI')

github_client = WebApplicationClient(GITHUB_CLIENT_ID)

GITHUB_AUTHORIZATION_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"

templates = Jinja2Templates(directory="templates")

@router.get("/login")
async def github_login(request: Request):
    state = str(uuid.uuid4())
    request.session["state"] = state

    authorization_url = github_client.prepare_request_uri(
        GITHUB_AUTHORIZATION_URL,
        redirect_uri=GITHUB_REDIRECT_URI,
        state=state,
    )
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def github_callback(request: Request):
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    if not code or not state:
        raise HTTPException(status_code=400, detail="Invalid callback request")

    if state != request.session.get("state"):
        raise HTTPException(status_code=400, detail="Invalid state")

    try:
        token_url, headers, body = github_client.prepare_token_request(
            GITHUB_TOKEN_URL,
            authorization_response=str(request.url),
            redirect_url=GITHUB_REDIRECT_URI,
            code=code
        )
        token_response = requests.post(token_url, headers=headers, data=body, auth=(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET))
        token_response.raise_for_status()
        token_data = github_client.parse_request_body_response(token_response.text)

        userinfo_endpoint, headers, _ = github_client.add_token(GITHUB_USERINFO_URL)
        userinfo_response = requests.get(userinfo_endpoint, headers=headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

        # Notify WebSocket clients about the login success
        #await notify_clients(f"User {user_info['login']} logged in successfully")
        print(user_info)    
        return templates.TemplateResponse("github_profile.html", {"request": request, "user_info": user_info})
        #return {"message": "User logged in successfully", "user_info": user_info}
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Error fetching user info")
