"""URL mappong for recipe service/app"""

from django.urls import (
    path,
    include,
)

from recipe.views import RecipeViewSet, TagViewSet

from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
