from django.db.models import Count
from rest_framework import serializers
from rest_framework.authtoken.admin import User
from django_countries.serializers import CountryFieldMixin

from ..models import *


# Serializers define the API representation.
# User Serializer
class UserSerializer(serializers.ModelSerializer, CountryFieldMixin):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}
        depth = 0

    def save(self):
        user = User(first_name=self.validated_data['first_name'],
                    last_name=self.validated_data['last_name'],
                    username=self.validated_data['username'],
                    email=self.validated_data['email'])
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)


class UserProfileSerializer(serializers.ModelSerializer, CountryFieldMixin):
    class Meta:
        model = UserProfile
        fields = '__all__'
        depth = 0


### Movie Serializer
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'
        depth = 0


# Comments serializer
class CommentSerializer(serializers.ModelSerializer, CountryFieldMixin):
    movie = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ['user', 'comment', 'movie']
        depth = 1


class MovieCommentSerializer(serializers.ModelSerializer, CountryFieldMixin):
    movie_comments = CommentSerializer(many=True)

    class Meta:
        model = Movie
        fields = '__all__'
        depth = 1


class MovieCastSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieCast
        fields = '__all__'
        depth = 1


class ActivitySerializer(serializers.ModelSerializer):
    # activity = serializers.RelatedField(many=True)

    class Meta:
        model = Activity
        fields = '__all__'
        depth = 2


class BlockListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockList
        fields = '__all__'
        depth = 1


class WatchList(serializers.ModelSerializer):
    class Meta:
        model = WatchList
        fields = '__all__'
        depth = 1


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'
        depth = 2


class RatingSerializer(serializers.ModelSerializer):
    rate_count_dict = Rating.objects.values('rating').annotate(rate_count=Count('rating'))

    class Meta:
        model = Rating
        fields = '__all__'
        depth = 1


class MovieLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieLink
        fields = '__all__'
        depth = 1
