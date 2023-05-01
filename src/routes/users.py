from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session


from src.database.db import get_db
from src.repository import user as repository_users
from src.services.auth import AuthToken
from src.schemas import UserResponse
from src.services.cloudinary import CloudImage

cloud_image = CloudImage()

authtoken = AuthToken()
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: int = Depends(authtoken.get_current_user), db: Session = Depends(get_db) ):
    """
    The read_users_me function is a GET request that returns the user's information.
    The current_user parameter is an integer value that represents the user's ID.
    The db parameter is a Session object from SQLAlchemy.

    :param current_user: int: Get the current user id from the authtoken
    :param db: Session: Pass the database session to the repository layer
    :return: The user object of the current user
    :doc-author: Trelent
    """
    return await repository_users.get_user_by_id(current_user, db)


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: int = Depends(authtoken.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function updates the avatar of a user.
    The function takes in an UploadFile object, which is a file that has been uploaded to the server.
    It also takes in the current_user and db objects as dependencies.

    :param file: UploadFile: Get the file from the request
    :param current_user: int: Get the current user's id
    :param db: Session: Get the database session
    :return: The user object that has been updated with the new avatar
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_id(current_user, db)
    route = cloud_image.get_name(user.email)
    r = cloud_image.upload(file.file, route)
    src_url = cloud_image.get_url_for_avatar(route, r)
    user = await repository_users.update_avatar(user, src_url, db)
    return user
