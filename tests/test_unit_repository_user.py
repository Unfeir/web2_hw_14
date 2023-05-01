import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.user import (
    get_user_by_email,
    get_user_by_id,
    add_user,
    update_token,
    update_reset_token,
    update_password,
    verify_email,
    update_avatar,

)


class TestUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email(self):
        user = User()
        print(user)
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=user.email, db=self.session)
        print(result)
        self.assertEqual(result, user)

    async def test_get_user_by_id(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_id(userid=1, db=self.session)
        self.assertEqual(result, user)

    async def test_add_user(self):
        user = UserModel(username='Test', email='example@mail.com', password='qwerty')
        result = await add_user(body=user, db=self.session)
        self.assertTrue(hasattr(result, 'id'))
        self.assertEqual(result.username, user.username)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.password, user.password)

    async def test_update_token(self):
        user = User()
        await update_token(user=user, refresh_token='refresh', db=self.session)
        self.assertEqual(user.refresh_token, 'refresh')

    async def test_update_reset_token(self):
        user = User()
        await update_reset_token(user=user, reset_token='reset', db=self.session)
        self.assertEqual(user.password_reset_token, 'reset')

    async def test_update_password(self):
        user = User()
        await update_password(user=user, new_password='123456', db=self.session)
        self.assertEqual(user.password, '123456')

    async def test_verify_email(self):
        user = User()
        await verify_email(user=user, db=self.session)
        self.assertEqual(user.email_confirm, True)

    async def test_update_avatar(self):
        user = User()
        await update_avatar(user=user, url='fake.url', db=self.session)
        self.assertEqual(user.avatar, 'fake.url')


if __name__ == '__main__':
    unittest.main()
