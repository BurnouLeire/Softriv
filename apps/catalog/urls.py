from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CatalogoViewSet

router = DefaultRouter()
router.register(r'servicios', CatalogoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
