from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views
from .views import *
from django.urls import path, include

app_name = 'moviesapp'

# router = routers.DefaultRouter()
# router.register('movielist/add', ManageViewSet, basename='movielist'),
# router.register('guest', ReadOnlyViewSet, basename='guest')

urlpatterns = [
    # path('', include(router.urls)),
    # path('movies/', views.movie_list),
    # path('movies/<int:pk>/delete', views.delete_movie),
    # path('movies/add', views.add_movie, name='add_movie'),
    # path('movies/<int:pk>/', views.movie_list),
    # path('movies/<int:pk>/edit', views.edit_movie),
    path('token/', obtain_auth_token),
    path("signout/", views.sign_out),
    path('register/', views.register),
    path("users/current/", views.current_user),
    path("user_profile/current", views.user_profile),
    path("cast", views.movie_cast),
    path("cast/<int:pk>", views.movie_cast),

    path("rating_detail/<int:pk>/", views.rating_detail),
    path("rating/<int:pk>/", views.rate_movie),
    path("movies/<int:pk>/", views.MovieDetailsView.as_view()),
    path("movies/", views.MovieAPIView.as_view()),


    path("comments/", views.comments_list),
    path("comments/<str:slug>", views.comments_detail),

    #Search
    path('search/', MovieSearch.as_view(), name='movie_search'),

    # api
    path("api/moviedetails/<str:pk>", MovieDetails.as_view()),
    path("api/movielist", MovieList.as_view()),
    path("api/search", MovieSearch.as_view()),





]

