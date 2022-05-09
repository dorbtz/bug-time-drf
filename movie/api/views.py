import math
from getpass import getpass

import requests
from django.contrib.auth.decorators import login_required
from django.core.mail.backends import console
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from rest_framework import viewsets, status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, MovieSerializer, UserProfileSerializer, CommentSerializer, RatingSerializer, \
    MovieCastSerializer
from ..models import Movie, UserProfile, Rating, Comment, Activity, Person, MovieLink, MovieCast
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

MOVIES_PER_PAGE = 20
USERS_PER_PAGE = 10


# Search View
class MovieSearch(ListView):
    model = Movie
    paginate_by = MOVIES_PER_PAGE

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            object_list = self.model.objects.filter(title__icontains=query)

        else:
            object_list = self.model.objects.none()

        return object_list


# Admin View
class ManageViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


# Movies View
class MovieList(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MovieDetails(DetailView):
    permission_classes = [AllowAny]
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()

    def get_object(self):
        object = super(MovieDetails, self).get_object()
        object.views_count += 1
        object.save
        return object

    def get_context_data(self, **kwargs):
        context = super(MovieDetails, self).get_context_data(**kwargs)
        context['links'] = MovieLink.objects.filter(movie=self.get_object())
        context['related_movies'] = Movie.objects.filter(category=self.get_object().category)
        print(context['related_movies'])
        return context


# Get Methods
# @login_required
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def movie_cast(request, pk=None):
    method = request.method
    try:
        casts = MovieCast.objects.all().order_by('movie', 'person')
    except MovieCast.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if pk is not None:
        cast = MovieCast.objects.get(pk=pk)
        serializer = MovieCastSerializer(cast, many=True)
        return Response(serializer.data)

    if method == 'GET':
        cast_filter = casts

        if 'person' in request.GET and request.GET['person']:
            cast_filter = cast_filter.filter(Q(slug=request.GET['person']))
            serializer = MovieCastSerializer(cast_filter, many=True)
            console.log(serializer)
            return Response(serializer.data)

        if 'movie' in request.GET and request.GET['movie']:
            cast_filter = cast_filter.filter(Q(category=request.GET['movie']))
            serializer = MovieCastSerializer(cast_filter, many=True)
            console.log(serializer)
            return Response(serializer.data)
        else:
            serializer = MovieCastSerializer(cast_filter, many=True)
            return Response(serializer.data)


class MovieAPIView(APIView):

    def get(self, request):

        s = request.GET.get('s')

        language = request.GET.get('language')
        category = request.GET.get('category')
        status = request.GET.get('status')
        print(category)
        sort = request.GET.get('sort')
        page = int(request.GET.get('page', 1))
        per_page = 5

        movies = Movie.objects.all()

        if s:
            movies = movies.filter(Q(title__icontains=s) |
                                   Q(category__icontains=s))
        if sort == 'asc':
            movies = movies.order_by('title')
        elif sort == 'desc':
            movies = movies.order_by('-title')

        if category:
            movies = movies.filter(category__icontains=category)
        if language:
            movies = movies.filter(language__icontains=language)
        if status:
            movies = movies.filter(status__icontains=status)
        total = movies.count()
        start = (page - 1) * per_page
        end = page * per_page
        serializer = MovieSerializer(movies[start:end], many=True)

        return Response({
            'data': serializer.data,
            'total': total,
            'page': page,
            'last_page': math.ceil(total / per_page)

        })


class MovieDetailsView(APIView):
    def get(self, request, pk):
        if request.method == 'GET':
            movie = Movie.objects.get(pk=pk)
            serializer = MovieSerializer(movie, many=False)
            return Response(serializer.data)

    def put(self, request, pk):
        if request.method == 'PUT':
            movie = Movie.objects.get(pk=pk)
            serializer = MovieSerializer(movie, data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.save()
                data['success'] = 'update successfully'
                return Response(data=data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.method == 'DELETE':
            movie = Movie.objects.get(pk=pk)
            movie.delete()
            return Response(200)


# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# def movie_list(request, pk=None):
#     method = request.method
#     try:
#         movies = Movie.objects.all()
#     except Movie.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if method == 'GET':
#         movies_filter = movies
#
#         title = request.GET.get('title')
#         sort = request.GET.get('sort')
#         page = int(request.GET.get('page', 1))
#         per_page = 5
#
#         if sort == 'asc':
#             movies = movies.order_by('category')
#         elif sort == 'desc':
#             movies = movies.order_by('-category')
#
#         if title:
#             movies = movies.filter(title__title_name__icontains=title)
#         total_movies = Movie.count()
#         start = (page - 1) * per_page
#         end = page * per_page
#         serializer = MovieSerializer(movies[start:end], many=True)
#
#         if pk is not None:
#             # detail view
#             movie = Movie.objects.get(pk=pk)
#             # slug =Movie.objects.get(slug=slug)
#             serializer = MovieSerializer(movie, many=False)
#             return Response(serializer.data)
#
#         if 'slug' in request.GET and request.GET['slug']:
#             movies_filter = movies_filter.filter(Q(slug=request.GET['slug']))
#             serializer = MovieSerializer(movies_filter, many=True)
#             console.log(serializer)
#
#         if 'category' in request.GET and request.GET['category']:
#             movies_filter = movies_filter.filter(Q(category=request.GET['category']))
#             serializer = MovieSerializer(movies_filter, many=True)
#             console.log(serializer)
#
#         if 'status' in request.GET and request.GET['status']:
#             movies_filter = movies_filter.filter(Q(status=request.GET['status']))
#             serializer = MovieSerializer(movies_filter, many=True)
#             console.log(serializer)
#
#         if 'language' in request.GET and request.GET['language']:
#             movies_filter = movies_filter.filter(Q(language=request.GET['language']))
#             serializer = MovieSerializer(movies_filter, many=True)
#             console.log(serializer)
#
#         if 'year_of_production' in request.GET and request.GET['year_of_production']:
#             movies_filter = movies_filter.filter(Q(request.GET['year_of_production']))
#             serializer = MovieSerializer(movies_filter, many=True)
#
#         return Response({
#             'data': serializer.data,
#             'total': total_movies,
#             'page': page,
#             'last_page': math.ceil(total / per_page)
#         })

# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsAdminUser])
# def movie_detail(request, pk):
#     movie = Movie.objects.get(pk=pk)
#     serializer = MovieSerializer(movie, many=False)
#     return Response(serializer.data)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
def comments_list(request):
    if request.method == 'GET':
        all_comments = Comment.objects.all().order_by('user', 'movie')
        if 'user' in request.GET and request.GET['user']:
            all_comments = all_comments.filter((Q(user=request.GET['user'])))
        if 'movie' in request.GET and request.GET['movie']:
            all_comments = all_comments.filter((Q(movie=request.GET['movie'])))
        serializer = CommentSerializer(all_comments, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        user = request.data["user"]
        movie = request.data["movie"]
        comment = request.data["comment"]
        created = request.data["created_at"]
        new_comment = Comment(user=user, comment=comment, movie=movie, created=created)
        new_comment.save()
        return Response(status=status.HTTP_201_CREATED)

    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def comments_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    comments = movie.movie_comments.filter(active=True)
    new_comment = None
    # Comment posted commit=False
    if request.method == 'POST':
        comment_serializer = CommentSerializer(data=request.data)
        if comment_serializer.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_serializer.save()
            # Assign the current post to the comment
            new_comment.movie = movie
            # Save the comment to the database
            new_comment.save()
    else:
        comment_serializer = CommentSerializer()

    return render(request, {'movie': movie,
                            'comments': comments,
                            'new_comment': new_comment,
                            'comment_serializer': comment_serializer})


# POST Methods

# @login_required
@permission_classes([IsAdminUser])
@api_view(['POST', 'GET'])
def add_movie(request):
    if request.method == 'GET':
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = MovieSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            movie = serializer.save()
            data['response'] = "successfully added"
            data['title'] = movie.title
        else:
            data = serializer.errors
        return Response(data)


@api_view(['GET'])
def rating_detail(request, pk):
    ratings = Rating.objects.filter(movie=pk)
    serializer = RatingSerializer(ratings, many=True)
    total = (len(serializer.data))
    total_ratings = 0
    for i in range(total):
        # print(serializer.data[i]['rating'])
        total_ratings += serializer.data[i]['rating']
    avg_rate = 0
    try:
        avg_rate = str(total_ratings / total)[:3]
    except:
        pass
    # print(avg_rate)
    return Response({'avg_rate': avg_rate})


@api_view(['POST', 'PUT', 'DELETE'])
def rate_movie(request, pk):
    serializer = RatingSerializer(movie=pk, data=request.data)

    if request.method == 'POST':
        data = {}
        if serializer.is_valid():
            rating = serializer.save()
            data['response'] = "successfully rated"
            data['rating'] = rating.rating
        else:
            data = serializer.errors
        return Response(data)
    if request.method == 'PUT':
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['success'] = 'rating is updated successfully'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        rating = Rating.objects.get(pk=pk)
        rating.delete()
        return Response(200)


# Watchlist View
def watchlist_view(request, username):
    profile = get_object_or_404(User, username=username)

    watchlist = profile.watchlist.all().order_by('-important', '-movie__release_date')
    movies_list = [w.movie for w in watchlist]
    movies_count = profile.watchlist.all().count()

    paginator = Paginator(movies_list, MOVIES_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = []  # paginator.page(paginator.num_pages)

    data = []
    for movie in movies:
        data.append(movie_to_dict(movie))

    return JsonResponse({
        "status": "200",
        "count": int(len(data)),
        "total": int(movies_count),
        "page": int(page),
        "movies": data,
    })


# Watchlist add or remove movie
# @login_required
# def watchlist_add_remove(request):
#     id = request.POST.get('id', None)
#     movie = get_object_or_404(Movie, pk=id)
#     exists = request.user.watchlist.filter(movie=movie)
#     if exists:
#         exists.delete()
#         Activity.add(request.user, movie, 'watchlist_remove')
#         return HttpResponse("removed")
#     else:
#         watchlist = Watchlist()
#         watchlist.user = request.user
#         watchlist.movie = movie
#         watchlist.save()
#         # delete from history
#         history = request.user.history.filter(movie=movie)
#         history.delete()
#         # delete from blocklist
#         Activity.add(request.user, movie, 'watchlist_add')
#         return HttpResponse("added")


# person view
# @login_required
# def person_view(request, person_id):
#     person = get_object_or_404(Person, pk=person_id)
#     movies_list = person.movies.all().order_by('-year_of_production')
#     movies_count = movies_list.count()
#
#     paginator = Paginator(movies_list, MOVIES_PER_PAGE)
#     page = request.GET.get('page')
#     try:
#         movies = paginator.page(page)
#     except PageNotAnInteger:
#         movies = paginator.page(1)
#     except EmptyPage:
#         movies = paginator.page(paginator.num_pages)
#
#     percentage = 0
#     history_count = 0
#     if request.user.is_authenticated():
#         history_count = request.user.history.filter(movie__cast=person).count()
#         percentage = int(float(history_count) / float(movies_count) * 100)
#
#     context = {
#         'person': person,
#         'movies': movies,
#         'count': movies_count,
#         'history_count': history_count,
#         'percentage': percentage,
#     }
#     return render(request, 'person.html', context)


# DELETE Method
# @login_required
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
def delete_movie(request, pk):
    if request.method == 'DELETE':
        movie = Movie.objects.get(pk=pk)
        movie.delete()
        return Response(200)


@login_required
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def comment_details(request, pk):
    if request.method == 'DELETE':
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return Response(200)


# PUT Method
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
def edit_movie(request, pk):
    try:
        movie = Movie.objects.get(movie=request.movie, pk=pk)
    except movie.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = MovieSerializer(movie, data=request.data)
    data = {}
    if serializer.is_valid():
        serializer.save()
        data['success'] = 'update successfully'
        return Response(data=data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
@api_view(['PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def edit_comment(request, user_id):
    try:
        comment = Comment.objects.get(comment=request.comment, user_id=user_id)
    except comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = CommentSerializer(comment, data=request.data)
    data = {}
    if serializer.is_valid():
        serializer.save()
        data['success'] = 'update successfully'
        return Response(data=data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# obtain_auth_token = ObtainAuthToken.as_view()


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def current_user(request):
    curr_user = request.user
    data = {
        "first_name": curr_user.first_name,
        "last_name": curr_user.last_name,
        "id": curr_user.id,
        "username": curr_user.username
    }
    return Response(data)


@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_profile(request):
    try:
        user = UserProfile.objects.get(user=request.user.id)
    except:
        user = UserProfile(user=request.user)
        user.save()
    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    if request.method == 'PUT':
        serializer = UserProfileSerializer(instance=user, data=request.data['profile'])
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        print(request.data)
        serializer = UserSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data['response'] = "successfully added"
            data['username'] = user.username
            data['password'] = user.password
            token = Token.objects.get(user=user).key
            data['token'] = token
        else:
            data = serializer.errors
        return Response(data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def sign_out(request):
    token1 = Token.objects.get(key=request.auth)
    token1.delete()
    return Response("Logout Successfully")
