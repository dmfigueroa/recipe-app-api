"""
Serializers for the recipe app
"""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for a recipe"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'title',
            'time_minutes',
            'price',
            'link'
        )
        read_only_fields = ('id',)


class RecipeDetailSerializers(RecipeSerializer):
    """Serializer for a recipe detail"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('description',)
