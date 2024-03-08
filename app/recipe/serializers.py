"""
Serializer for the Recipe Model.
"""

from core.models import Recipe
from rest_framework import serializers


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe model."""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    "Serializer for recipe Details"

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
