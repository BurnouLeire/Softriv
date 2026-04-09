from django.urls import path
from .views import CustomLoginView, CreateUserView, ProfileView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('users/create/', CreateUserView.as_view(), name='create-user'),
    path('users/profile/', ProfileView.as_view()),


]
