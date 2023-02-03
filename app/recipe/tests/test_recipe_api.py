"""
Tests for recipe API
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, User
from core.utils import get_user_model

from recipe.serializers import RecipeSerializer, RecipeDetailSerializers

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""

    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user: User, **params):
    """Helper function to create a recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def create_user(**params):
    """Helper function to create a user"""

    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Tests for public recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_recipe_list_limited_to_user(self):
        """Test retrieving recipes for the current user"""

        other_user = create_user(
            email='other@example.com',
            password='password123'
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_get_recipe_detail(self):
        """Test retrieving a recipe detail"""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.pk)
        res = self.client.get(url)

        serializer = RecipeDetailSerializers(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_create_recipe(self):
        """Test creating a recipe"""

        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': Decimal('5.00'),
            'description': 'Sample description',
            'link': 'http://example.com/recipe.pdf',
        }

        res = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(pk=res.data['id'])  # type: ignore

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe"""

        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Chocolate cheesecake',
            link=original_link,
        )

        payload = {'title': 'New title'}
        url = detail_url(recipe.pk)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe"""

        recipe = create_recipe(
            user=self.user,
            title='Chocolate cheesecake',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description',
        )

        payload = {
            'title': 'New title',
            'time_minutes': 30,
            'price': Decimal('10.00'),
            'description': 'Sample description',
            'link': 'http://example.com/recipe.pdf',
        }

        url = detail_url(recipe.pk)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def delete_recipe(self):
        """Test deleting a recipe"""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.pk)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(pk=recipe.pk).exists())

    def test_delete_other_users_recipe_error(self):
        """Test that a user cannot delete another user's recipe"""

        other_user = create_user(
            email='user2@example.com',
            password='password123'
        )
        recipe = create_recipe(user=other_user)

        url = detail_url(recipe.pk)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(pk=recipe.pk).exists())
