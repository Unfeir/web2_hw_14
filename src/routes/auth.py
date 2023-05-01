from fastapi import Depends, HTTPException, status, APIRouter, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, Token, RequestEmail, ResetPassword
from src.repository import user as repository_user
from src.services.auth import AuthPassword, AuthToken
from src.services.email import send_email, pass_reset_email

router = APIRouter(prefix="/auth", tags=['auth'])
security = HTTPBearer()
authpassword = AuthPassword()
authtoken = AuthToken()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             description='Create new user')
async def sign_up(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The sign_up function creates a new user in the database.
    It takes a UserModel object as input, and returns the newly created user.
    If an email is already in use, it raises an HTTP 409 Conflict error.

    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the server
    :param db: Session: Get the database session
    :return: A usermodel object
    :doc-author: Trelent
    """
    check_user = await repository_user.get_user_by_email(body.email, db)
    if check_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This email is already in use')

    body.password = authpassword.get_hash_password(body.password)
    new_user = await repository_user.add_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=Token)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    It takes the email and password of the user as input,
    and returns an access token if authentication was successful.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Pass the database session to the function
    :return: A dictionary with the access_token, refresh_token and token type
    :doc-author: Trelent
    """
    user = await repository_user.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not authpassword.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if not user.email_confirm:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"check {user.email} to Confirm account")

    access_token = await authtoken.create_access_token(data={"sub": user.email})
    refresh_token = await authtoken.create_refresh_token(data={"sub": user.email})
    await repository_user.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh_token", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
    The function takes in a refresh token and returns a new access_token,
    refresh_token, and the type of token (bearer).

    :param credentials: HTTPAuthorizationCredentials: Get the token from the header
    :param db: Session: Pass the database session to the function
    :return: A dict with the access_token, refresh_token and token_type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await authtoken.refresh_token_email(token)
    user = await repository_user.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_user.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await authtoken.create_access_token(data={"sub": email})
    refresh_token = await authtoken.create_refresh_token(data={"sub": email})
    await repository_user.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
    It takes in the token that was sent to the user's email and uses it to get their email address.
    Then, it gets the user from our database using their email address and checks if they exist.
    If they don't exist, we return an error message saying &quot;Verification error&quot;.
    Otherwise, we check if their account has already been verified by checking if 'email_confirm' is True or False
    (True means that it has been confirmed).
    If 'email_confirm' is True, then we return a message

    :param token: str: Get the email from the token
    :param db: Session: Get the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    email = await authtoken.get_email_from_token(token)
    user = await repository_user.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.email_confirm:
        return {"message": "Your email is already confirmed"}
    await repository_user.verify_email(user, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that they can click on
    to confirm their email address. The function takes in a RequestEmail object, which contains the
    email of the user who wants to confirm their account. It then checks if there is already a confirmed
    user with that email address, and if so returns an error message saying as much. If not, it sends them
    an email containing a link they can click on.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Access the database
    :return: A message that the user should check their email for confirmation
    :doc-author: Trelent
    """
    user = await repository_user.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.post('/password_reset')
async def password_reset(email: str, background_tasks: BackgroundTasks, request: Request,
                         db: Session = Depends(get_db)):
    """
    The password_reset function is used to send a password reset email to the user.
    It takes in an email address and sends a password reset link to that address.
    The function also requires background_tasks, request, and db as parameters.

    :param email: str: Get the email of the user that wants to reset his password
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Get the database session
    :return: A string
    :doc-author: Trelent
    """
    user = await repository_user.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no user with such email')

    background_tasks.add_task(pass_reset_email, user.email, user.username, request.base_url)
    return f'Reset instruction was sending to {email}'


@router.get('/password_reset_confirm/{token}')
async def password_reset_email(token: str, db: Session = Depends(get_db)):
    """
    The password_reset_email function is used to send a password reset email to the user.
    The function takes in a token and db as parameters, where the token is generated by
    authtoken.create_reset_password_token() and passed into this function from the frontend,
    while db is an instance of Session that allows us to access our database through SQLAlchemy's ORM.

    :param token: str: Get the email from the token
    :param db: Session: Get a database session
    :return: A dictionary with a reset_token key
    :doc-author: Trelent
    """
    email = await authtoken.get_email_from_token(token)
    user = await repository_user.get_user_by_email(email, db)
    reset_password_token = await authtoken.create_reset_password_token(data={"sub": user.email})
    await repository_user.update_reset_token(user, reset_password_token, db)
    return {'reset_token': reset_password_token}


@router.post('/set_new_password')
async def password_reset(request: ResetPassword, db: Session = Depends(get_db)):
    """
    The password_reset function allows a user to reset their password.
    The function takes in the ResetPassword object, which contains the following fields:
    - reset_password_token (str): A token that is sent to the user's email address when they request a password reset.
    This token is used as an identifier for which account should have its password changed.
    - new_password (str): The new desired password for this account. Must be at least 8 characters long and contain at
    least one uppercase letter, lowercase letter, number and special character (!@#$%^&amp;*).


    :param request: ResetPassword: Get the reset_password_token and new password from the user
    :param db: Session: Get the database session
    :return: A string
    :doc-author: Trelent
    """
    token = request.reset_password_token
    email = await authtoken.reset_token_email(token)
    user = await repository_user.get_user_by_email(email, db)
    check_token = user.password_reset_token
    if check_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid reset token")
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="passwords do not match")

    new_password = authpassword.get_hash_password(request.new_password)
    await repository_user.update_password(user, new_password, db)
    await repository_user.update_reset_token(user, None, db)
    return 'password update successfully'
