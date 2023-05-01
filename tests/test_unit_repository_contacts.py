from datetime import date
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts,
    get_contact,
    search_contact,
    add_contact,
    change_contact,
    remove_contact,
    get_birthdays
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact()]
        self.session.query().filter_by().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user.id, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact(contact_id=contact.id, user=contact.user_id, db=self.session)
        self.assertEqual(contact, result)

    async def test_add_contact(self):
        user = ContactModel(first_name='First_name',
                            last_name='Last_name',
                            email='example@mail.com',
                            phone_number='0998887766',
                            birthday=date(year=1900, month=1, day=1),
                            address='Test_address',
                            user_id=1)
        result = await add_contact(body=user, user=1, db=self.session)
        self.assertTrue(hasattr(result, 'id'))
        self.assertEqual(result.first_name, user.first_name)
        self.assertEqual(result.last_name, user.last_name)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.birthday, user.birthday)
        self.assertEqual(result.address, user.address)

    async def test_change_contact(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        body = ContactModel(first_name='First_name',
                            last_name='Last_name',
                            email='example@mail.com',
                            phone_number='0998887766',
                            birthday=date(year=1900, month=1, day=1),
                            address='Test_address',
                            user_id=1)
        result = await change_contact(contact_id=contact.id, body=body, user=contact.user_id, db=self.session)
        self.assertEqual(contact, result)

    async def test_search_contact(self):
        contacts = [Contact(), Contact()]
        self.session.query().filter_by().all.return_value = contacts
        result = await search_contact(db=self.session, user=contacts[0].user_id,
                                      email=contacts[0].email)
        self.assertEqual(None, result)

    async def test_remove_contact(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await remove_contact(contact_id=contact.id, user=contact.user_id, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_birthdays(self):
        contacts = [Contact(birthday=date(year=1990, month=5, day=2)), Contact()]
        self.session.query().filter_by().all.return_value = contacts
        result = await get_birthdays(user=contacts[0].user_id, db=self.session)
        self.assertEqual([contacts[0]], result)


if __name__ == '__main__':
    unittest.main()
