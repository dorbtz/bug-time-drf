from django.views.generic import DetailView, ListView
from django.views.generic.dates import YearArchiveView
# Create your views here.
from .models import *


class HomesView(ListView):
    model = Movie
    # template_name = 'movie/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomesView, self).get_context_data(**kwargs)
        context['top_rated'] = Movie.objects.filter(status='top-rated')
        context['most_watched'] = Movie.objects.filter(status='most-watched')
        context['recently_added'] = Movie.objects.filter(status='recently-added')
        return context


class MovieList(ListView):
    model = Movie
    paginate_by = 2


class MovieDetail(DetailView):
    model = Movie

    def get_object(self):
        object = super(MovieDetail, self).get_object()
        object.views_count += 1
        object.save
        return object

    def get_context_data(self, **kwargs):
        context = super(MovieDetail, self).get_context_data(**kwargs)
        context['links'] = MovieLink.objects.filter(movie=self.get_object())
        context['related_movies'] = Movie.objects.filter(category=self.get_object().category)
        print(context['related_movies'])
        return context


class MovieCategory(ListView):
    model = Movie
    paginate_by = 1

    def get_queryset(self):
        self.category = self.kwargs['category']
        return Movie.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super(MovieCategory, self).get_context_data(**kwargs)
        context['movie_category'] = self.category
        return context


class MovieLanguage(ListView):
    model = Movie
    paginate_by = 2

    def get_queryset(self):
        self.language = self.kwargs['lang']
        return Movie.objects.filter(language=self.language)

    def get_context_data(self, **kwargs):
        context = super(MovieLanguage, self).get_context_data(**kwargs)
        context['movie_language'] = self.language
        return context


class MovieSearch(ListView):
    model = Movie
    paginate_by = 2

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            object_list = self.model.objects.filter(title__icontains=query)

        else:
            object_list = self.model.objects.none()

        return object_list


class MovieYear(YearArchiveView):
    queryset = Movie.objects.all()
    date_field = 'year_of_production'
    make_object_list = True
    allow_future = True

    paginate_by = 2





## old code from api.views


# @api_view(['GET'])
# def movie_details(request, movie_name):
#     if request.method == 'GET':
#         try:
#             movie = Movie.objects.get(name=movie_name)
#         except:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         serializer = MovieSerializer(movie)
#         return Response(serializer.data)


# @api_view(['GET', 'POST'])
# # @authentication_classes([TokenAuthentication])
# @permission_classes([IsAdminUser])
# def add_movie(request):
#     method = request.method
#     movies = Movie.objects.all()
#     if method == 'GET':
#         serializer = MovieSerializer(movies, many=True)
#         return Response(serializer.data)
#     if method == 'POST':
#         serializer = MovieSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# # @authentication_classes([TokenAuthentication])
# @permission_classes([IsAdminUser])
# def edit_movie(request, pk):
#     method = request.method
#     try:
#         movie = Movie.objects.get(pk=pk)
#     except Movie.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if method == 'GET':
#         serializer = MovieSerializer(movie, many=False)
#         return Response(serializer.data)
#
#     if method == 'PUT':
#         serializer = MovieSerializer(movie, data=request.data)
#         data = {}
#         if serializer.is_valid():
#             serializer.save()
#             data['success'] = 'update successfully'
#             return Response(data=data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# @api_view(['GET', 'POST'])
# # @authentication_classes([TokenAuthentication])
# @permission_classes([AllowAny])
# def movie_comment(request, pk):
#     movie = Movie.objects.get(pk)
#     if request.method == 'POST':
#         if 'comment' in request.data:
#             try:
#                 comment = Comment(movie=movie, comment=request.data['comment'])
#                 comment.save()
#                 serializer = MovieSerializer(Movie.objects.get(pk))
#                 return Response(serializer.data)
#             except:
#                 return Response({'status': 'failed'})
    # if request.method == 'GET':
    #     try:
    #         serializer = MovieSerializer(Movie.objects.get(id=id))
    #         comment = Comment(movie=request.data, id=id)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def MovieRatingView(request, id):
#     movie = Movie.objects.get(id=id)
#     if request.method == 'POST':
#         if 'rating' in request.data:
#             try:
#                 rating = Rating(movie=movie, rating=request.data['rating'])
#                 rating.save()
#                 serializer = MovieSerializer(Movie.objects.get(id=id))
#                 return Response(serializer.data)
#             except:
#                 return Response({'status': 'failed'})
#
#