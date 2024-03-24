from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .config import settings
from . import schemas, database, models, utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ACCESS_TOKEN_EXIPRATION_MINUTES = settings.access_token_expiration_minutes
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXIPRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credential_exception) -> schemas.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise credential_exception

        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credential_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception)

    db_user = db.query(models.User).filter(models.User.id == token.id).first()
    print(db_user)
    user = schemas.User.from_orm(
        db_user.__dict__
    )  # make use of a hashmap to get the user

    return user


def login(db: Session, username: str, password: str) -> str:
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User doesn't exist Credentials",
        )

    if not utils.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    # create token
    access_token = create_access_token({"user_id": user.id})
    return access_token


def signup(db: Session, user: schemas.CreateUser):
    query_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not query_user == None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email already exists",
        )
    hashed_password = utils.hash_password(
        user.password
    )  # hash the password passed through the json
    user.password = (
        hashed_password  # store the hashed password as the value to be added to the db
    )
    user = models.User(**user.dict())
    print(user.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def determine_login_or_signup(
    user: schemas.CreateUser,
    db: Session,
) -> schemas.User:
    user_exist = db.query(models.User).filter(models.User.email == user.email).first()
    if user_exist is None:
        # create user
        created_user = signup(db, user)
        user = schemas.User.from_orm(created_user.__dict__)
        return user
    else:
        user = schemas.User.from_orm(user_exist.__dict__)
        return user
