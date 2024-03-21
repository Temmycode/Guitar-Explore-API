from fastapi import HTTPException, Response, status, APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, oauth2
from typing import List

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.CreateUser, db: Session = Depends(database.get_db)):
    user = oauth2.signup(db, user)
    return user


@router.get("/", response_model=List[schemas.User])
def get_users(
    current_user: schemas.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
):
    users = db.query(models.User).all()
    return users
