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
    MovieCastSerializer, CommentTESTSerializer, RateMovieSerializer, CommentSerializers, CreateCommentSerializer, \
    CreateRatingSerializer
from ..models import Movie, UserProfile, Rating, Comment, Person, MovieLink, MovieCast, MovieComment
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken


class CreateMovieComment(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateCommentSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class CommentAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CommentSerializers

    def get_queryset(self, *args, **kwargs):
        movie_id = self.kwargs.get('id')
        qs = MovieComment.objects.filter(movie=movie_id).order_by("-created_at")
        return qs


class CreateRating(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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

        s = request.GET.get('search')

        language = request.GET.get('lang')
        category = request.GET.get('category')
        status = request.GET.get('status')
        year_of_production = request.GET.get('year')
        print(category)
        sort = request.GET.get('sort')
        page = int(request.GET.get('page', 1))
        per_page = 20

        movies = Movie.objects.all()

        if s:
            movies = movies.filter(Q(title__icontains=s) |
                                   Q(slug__icontains=s))
        if sort == 'asc':
            movies = movies.order_by('title')
        elif sort == 'desc':
            movies = movies.order_by('-title')

        if category:
            movies = movies.filter(category__icontains=category)
        if language:
            movies = movies.filter(language__icontains=language)
        if year_of_production:
            movies = movies.filter(year_of_production__icontains=year_of_production)
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


# class CommentsView(APIView):
#     def get(self, request):
#         all_comments = Comment.objects.all().order_by('user', 'movie')
#         if 'user' in request.GET and request.GET['user']:
#             all_comments = all_comments.filter((Q(user=request.GET['user'])))
#         if 'movie' in request.GET and request.GET['movie']:
#             all_comments = all_comments.filter((Q(movie=request.GET['movie'])))
#         serializer = CommentSerializer(all_comments, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         user = request.data["user"]
#         movie = request.data["movie"]
#         comment = request.data["comment"]
#         created = request.data["created_at"]
#         new_comment = Comment(user=user, comment=comment, movie=movie, created=created)
#         new_comment.save()
#         return Response(status=status.HTTP_201_CREATED)
#
#     def put(self, request, pk):
#         if request.method == 'PUT':
#             comment = Comment.objects.get(pk=pk)
#             serializer = CommentSerializer(comment, data=request.data)
#             data = {}
#             if serializer.is_valid():
#                 serializer.save()
#                 data['success'] = 'update successfully'
#                 return Response(data=data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         if request.method == 'DELETE':
#             comment = Comment.objects.get(pk=pk)
#             comment.delete()
#             return Response(200)


@api_view(['GET', 'POST'])
# @authentication_classes([TokenAuthentication])
def comments_list(request):
    if request.method == 'GET':
        all_comments = Comment.objects.all().order_by('movie')
        # if 'user' in request.GET and request.GET['user']:
        #     username = all_comments['username']
        #     all_comments = all_comments.filter((Q(user=request.GET[username])))
        if 'movie' in request.GET and request.GET['movie']:
            all_comments = all_comments.filter((Q(movie=request.GET['movie'])))
        # serializer = CommentSerializer(all_comments, many=True)
        serializer = CommentTESTSerializer(all_comments, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        user = request.user
        print(user)
        serializer = CommentSerializers(data=request.data, user=user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return HttpResponse("failed")

    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def comments_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    comments = movie.movie_comments.filter(active=True)
    user = request.user
    new_comment = None
    # Comment posted commit=False
    if request.method == 'GET':
        serializer = CommentTESTSerializer(comments, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        comment_serializer = CommentTESTSerializer(data=request.data)
        print('inside POST')
        if comment_serializer.is_valid():
            print('comment serializer is ok!')
            # Create Comment object but don't save to database yet
            new_comment = comment_serializer.save()
            # Assign the current post to the comment
            new_comment.movie = movie
            new_comment.user = user
            # Save the comment to the database
            new_comment.save()
            return Response(new_comment)
    else:
        comment_serializer = CommentTESTSerializer()

    # return Response({'movie': movie,
    #                  'comments': comments,
    #                  'new_comment': new_comment,
    #                  'comment_serializer': comment_serializer})
    return render(request, {'movie': movie,
                            'comments': comments,
                            'new_comment': new_comment,
                            'comment_serializer': comment_serializer})


# POST Methods

# @login_required
# @permission_classes([IsAdminUser])
@api_view(['POST', 'GET'])
def add_movie(request):
    print(request)
    if request.method == 'GET':
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        print("inside add movie")
        print(request.data)
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            print('entered is valid')
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.data, status.HTTP_404_NOT_FOUND)


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


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def rate_movie(request, pk):
    # serializer = RateMovieSerializer(pk, data=request.data)
    movie = get_object_or_404(Movie, pk=pk)
    user = request.user
    # rate = get_object_or_404(Rating, movie=pk)
    try:
        rate = Rating.objects.filter(movie=movie)
    except Rating.DoesNotExist:
        rate = Rating.objects.create(movie=movie)
        rate.save()

    if request.method == 'GET':
        # ratings = Rating.objects.filter(movie=pk)
        # ratings = Rating.objects.get(movie=pk)
        serialze = RateMovieSerializer(rate, many=True)
        return Response(serialze.data)

    if request.method == 'POST':
        serializer = RateMovieSerializer(data=request.data, user=user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)

    if request.method == 'PUT':
        rating = Rating.objects.get(movie=pk)
        serializer = RateMovieSerializer(rating, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['success'] = 'update successfully'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        rating = Rating.objects.get(pk=pk)
        rating.delete()
        return Response(200)


# Watchlist View
# def watchlist_view(request, username):
#     profile = get_object_or_404(User, username=username)
#
#     watchlist = profile.watchlist.all().order_by('-important', '-movie__release_date')
#     movies_list = [w.movie for w in watchlist]
#     movies_count = profile.watchlist.all().count()
#
#     paginator = Paginator(movies_list, MOVIES_PER_PAGE)
#     page = request.GET.get('page', 1)
#     try:
#         movies = paginator.page(page)
#     except PageNotAnInteger:
#         movies = paginator.page(1)
#     except EmptyPage:
#         movies = []  # paginator.page(paginator.num_pages)
#
#     data = []
#     for movie in movies:
#         data.append(movie_to_dict(movie))
#
#     return JsonResponse({
#         "status": "200",
#         "count": int(len(data)),
#         "total": int(movies_count),
#         "page": int(page),
#         "movies": data,
#     })


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
@authentication_classes([TokenAuthentication])
@api_view(['DELETE'])
def delete_movie(request, pk):
    if request.method == 'DELETE':
        movie = Movie.objects.get(pk=pk)
        movie.delete()
        return Response(200)


@login_required
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def comment_details(request, pk):
    if request.method == 'DELETE':
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return Response(200)


# PUT Method
@authentication_classes([TokenAuthentication])
@api_view(['PUT'])
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
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PUT', 'DELETE'])
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


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def current_user(request):
    curr_user = request.user
    data = {
        "first_name": curr_user.first_name,
        "last_name": curr_user.last_name,
        "id": curr_user.id,
        "username": curr_user.username
    }
    return Response(data)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET', 'PUT'])
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


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def sign_out(request):
    token1 = Token.objects.get(key=request.auth)
    token1.delete()
    return Response("Logout Successfully")
