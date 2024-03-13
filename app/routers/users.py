from fastapi import HTTPException, Response, status, APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.CreateUser, db: Session = Depends(database.get_db)):
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
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
