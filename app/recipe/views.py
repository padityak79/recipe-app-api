"""
Views for recipe API.
"""

from core.models import Recipe

from recipe.serializers import RecipeSerializer

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for the Recipe Model"""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """retrieve all recipe objects of an authenticated user"""
        return Recipe.objects.filter(user=self.request.user).order_by("-id")
