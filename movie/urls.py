from django.urls import path, include
from .views import *
app_name = 'movie'

urlpatterns = [

    # path('list_of_movies', MovieList.as_view(), name='movie_list'),
    # path('genres/<str:category>', MovieCategory.as_view(), name='movie_category'),
    # path('language/<str:lang>', MovieLanguage.as_view(), name='movie_language'),
    # # path('search/', MovieSearch.as_view(), name='movie_search'),
    # path('<slug:slug>', MovieDetail.as_view(), name='movie_detail'),
    # path('year/<int:year>', MovieYear.as_view(), name='movie_year'),

]


