"""
Tests for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import UserManager


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""

        email = 'test@example.com'
        password = 'testpass123'
        manager: UserManager = get_user_model().objects  # type: ignore
        user = manager.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            manager: UserManager = get_user_model().objects  # type: ignore
            user = manager.create_user(
                email=email,
                password='testpass123'
            )

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises ValueError"""

        with self.assertRaises(ValueError):
            manager: UserManager = get_user_model().objects  # type: ignore
            manager.create_user('', 'testpass123')

    def test_create_superuser(self):
        """Test creating a new superuser"""

        manager: UserManager = get_user_model().objects  # type: ignore
        user = manager.create_superuser(
            email='test@example.com',
            password='test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
