from fastapi import APIRouter, status, HTTPException, Depends, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from .. import utils, database, models, oauth2, config, schemas

router = APIRouter(tags=["Authentication"])
config = Config(".env")

oauth = OAuth(config)

oauth.register(  # register the app
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# Login with Google (Initiate authorization flow)
@router.get("/google-login")
async def google_login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


# Callback route to handle Google's response
@router.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return error
    user = token["userinfo"]
    if user:
        # add the user to the db if the user doesn't already exist
        print(user)
    return user


# login with email and password
@router.post("/login")
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    if not utils.verify_password(user_credentials.password, user.password):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    # create token
    access_token = oauth2.create_access_token({"user_id": user.id})
    message = {"access_token": access_token, "token_type": "bearer"}
    return JSONResponse(message)
