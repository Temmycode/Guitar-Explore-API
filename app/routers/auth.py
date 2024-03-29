from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .. import utils, database, oauth2, schemas
from ..config import settings
from google.oauth2 import id_token
from google.auth.transport import requests
import httpx

router = APIRouter(tags=["Authentication"])


@router.post("/google-signin", status_code=status.HTTP_200_OK, response_model=schemas.GoogleSignOutput)
async def login_with_google(token_id: schemas.GoogleSignIn, db: Session = Depends(database.get_db),):
    tokeninfo_url = "https://oauth2.googleapis.com/tokeninfo?id_token="
    async with httpx.AsyncClient() as client:
        try:
            idinfo = id_token.verify_oauth2_token(
                token_id.id_token,
                requests.Request(),
                settings.google_client_id,
            )  # verify jwt token
            user_id = idinfo["sub"]

            # get the user information from the tokeninfo endpoint from Google apis
            try:
                response = await client.get(f"{tokeninfo_url}{token_id.id_token}")
                if response.status_code == 200:
                    # if the response code is 200
                    # get the user information from the body
                    body = response.json()

                    # create a user and if the user is already created just return the user
                    user = schemas.CreateUser(
                        email=body["email"],
                        password=f"{body["name"]}{body["family_name"]}",
                        username=body["name"],
                        profile_picture=body["picture"],
                    )
                    db_user = await oauth2.determine_login_or_signup(user, db)
                    content = {"access_token": token_id.id_token, "token_type": "bearer", "user": db_user}
                    # return access token and the user_data as json response
                    return content
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Failed to fetch data from url",
                    )
            except Exception as err:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=err,
                )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Token",
            )




