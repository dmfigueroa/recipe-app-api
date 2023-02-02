"""
Serializers for the user API view
"""

from rest_framework import serializers

from core.utils import get_user_model


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password"""

        return get_user_model().objects.create_user(**validated_data)
