from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel


async def get_contacts(skip, limit, user: int, db: Session):
    """
    The get_contacts function returns a list of contacts for the user.
    Args:
    skip (int): The number of items to skip before starting to collect the result set.
    limit (int): The numbers of items to return.
    
    :param skip: Skip the first n contacts
    :param limit: Limit the number of contacts returned
    :param user: int: Filter the contacts by user_id
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user_id=user).offset(skip).limit(limit).all()
    return contacts


async def get_contact(contact_id, user: int, db: Session):
    """
    The get_contact function takes in a contact_id and user, and returns the contact with that id.
    Args:
    contact_id (int): The id of the desired Contact object.
    user (int): The id of the User who owns this Contact object.
    
    :param contact_id: Filter the database query to return only the contact with that id
    :param user: int: Filter the contact by user_id
    :param db: Session: Pass the database session to the function
    :return: The contact with the given id and user_id
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id, user_id=user).first()
    return contact


async def search_contact(db: Session, user: int, first_name=None, last_name=None, email=None):
    """
    The search_contact function searches for a contact in the database.
    Args:
    db (Session): The database session to use.
    user (int): The id of the user who owns this contact.
    first_name (str, optional): The first name of the contact to search for. Defaults to None if not provided by caller. 
    If provided, will be capitalized before searching in DB as all names are stored capitalized in DB for consistency and ease of searching/sorting later on when displaying contacts list or performing other operations on contacts list such as sorting alphabetically by last name then first name
    
    :param db: Session: Pass in the database session
    :param user: int: Filter the contacts by user_id
    :param first_name: Filter the contacts by first name
    :param last_name: Filter the contacts by last name
    :param email: Find a contact by email
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = None
    if first_name and last_name:
        contacts = db.query(Contact).filter_by(first_name=first_name.capitalize(), last_name=last_name.capitalize(),
                                               user_id=user).all()
    if first_name:
        contacts = db.query(Contact).filter_by(first_name=first_name.capitalize(), user_id=user).all()
    if email:
        contacts = db.query(Contact).filter_by(email=email.lower(), user_id=user).all()

    return contacts


async def add_contact(body: ContactModel, user: int, db: Session):
    """
    The add_contact function creates a new contact in the database.

    :param body: ContactModel: Get the information from the request body
    :param user: int: Pass in the user id of the logged in user
    :param db: Session: Pass the database session to the function
    :return: The contact that was added to the database
    :doc-author: Trelent
    """
    contact = Contact(first_name=body.first_name.capitalize(),
                      last_name=body.last_name.capitalize(),
                      email=body.email,
                      phone_number=body.phone_number,
                      birthday=body.birthday,
                      address=body.address,
                      user_id=user)

    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def change_contact(contact_id, body, user: int, db: Session):
    """
    The change_contact function takes in a contact_id, body, user and db.
    It then gets the contact from the database using get_contact function.
    If there is a contact it changes its first name to that of the body's first name, last name to that of
    the body's last name and so on for birthday, email and address. It then commits these changes to the database.

    :param contact_id: Identify the contact to be deleted
    :param body: Get the data from the request body,
    :param user: int: Get the user id from the token
    :param db: Session: Pass the database session to the function
    :return: The contact object
    :doc-author: Trelent
    """
    contact = await get_contact(contact_id, user, db)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.birthday = body.birthday
        contact.email = body.email
        contact.address = body.address
        db.commit()
    return contact


async def remove_contact(contact_id, user: int, db: Session):
    """
    The remove_contact function removes a contact from the database.
    Args:
    contact_id (int): The id of the contact to be removed.
    user (int): The id of the user who owns this contact.

    :param contact_id: Find the contact in the database
    :param user: int: Get the user id from the token
    :param db: Session: Pass the database session to the function
    :return: The contact that was removed
    :doc-author: Trelent
    """
    contact = await get_contact(contact_id, user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_birthdays(user: int, db: Session):
    """
    The get_birthdays function takes in a user id and a database session. It then queries the database for all contacts
    associated with that user, and returns those contacts whose birthdays are within 7 days of today.

    :param user: int: Filter the contacts by user_id
    :param db: Session: Access the database
    :return: A list of contacts whose birthdays are within the next 7 days
    :doc-author: Trelent
    """
    today = date.today()
    delta = timedelta(days=7)
    all_contacts = db.query(Contact).filter_by(user_id=user).all()
    contacts = []
    for contact in all_contacts:
        if contact.birthday:
            if contact.birthday.replace(year=today.year) >= today and contact.birthday.replace(
                    year=today.year) <= today + delta:
                contacts.append(contact)
    return contacts
