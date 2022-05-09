from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone
from django_countries.fields import CountryField
from multiselectfield import MultiSelectField
# Create your models here.
from rest_framework.authtoken.models import Token

CATEGORY_CHOICES = (
    ('action', 'ACTION'),
    ('adventure', 'ADVENTURE'),
    ('animated', 'ANIMATED'),
    ('comedy', 'COMEDY'),
    ('crime', 'CRIME'),
    ('drama', 'DRAMA'),
    ('fantasy', 'FANTASY'),
    ('horror', 'HORROR'),
    ('historical', 'HISTORICAL'),
    ('romance', 'ROMANCE'),
    ('western', 'WESTERN'),
    ('science-fiction', 'SCIENCE FICTION'),

)

LANGUAGE_CHOICES = (
    ('english', 'ENGLISH'),
    ('hebrew', 'HEBREW'),
    ('spanish', 'SPANISH'),
)

STATUS_CHOICES = (
    ('recently-added', 'RECENTLY ADDED'),
    ('most-watched', 'MOST WATCHED'),
    ('top-rated', 'TOP RATED'),
)

GENDER = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('none', 'None')
)


# def upload_to(instance, filename)

class Person(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    profile_path = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(default='persons/person-no-available.jpg', blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    known_for_department = models.CharField(max_length=100, blank=True, null=True)
    death = models.DateField(blank=True, null=True, default=None)
    also_known_as = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(choices=GENDER, max_length=10, blank=True, null=True)
    biography = models.TextField(max_length=1000, blank=True, null=True)
    place_of_birth = models.CharField(max_length=255, blank=True, null=True)

    # def url(self):
    #     return '/person/{}/'.format(self.id)
    class Meta:
        db_table = 'person'

    # def images(self):
    #     if self.image:
    #         return '/media/persons/'.format(self.image)
    #     return '/media/persons/person.png'

    # def portrait(self):
    #     if self.profile_path:
    #         return 'https://image.tmdb.org/t/p/w300_and_h450_bestv2/{}'.format(self.profile_path)
    #     return '/static/img/person.png'

    def __str__(self):
        return f"{self.name}"


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True)
    image = models.ImageField(default='movies/poster-not-available.jpg', blank=True, null=True)
    banner = models.ImageField(default='banners/no-banner-available.jpg', blank=True, null=True)
    category = MultiSelectField(choices=CATEGORY_CHOICES, max_choices=4, blank=True)
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=20, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, blank=True)
    director = models.CharField(max_length=100, null=True, blank=True)
    cast = models.ManyToManyField(Person, through='MovieCast', related_name='movies', blank=True)
    year_of_production = models.DateField()
    views_count = models.IntegerField(default=0, blank=True, null=True)
    movie_trailer = models.URLField(blank=True)

    created = models.DateTimeField(default=timezone.now)

    slug = models.SlugField(blank=True, null=True)

    def banners(self, *args, **kwargs):
        if self.banner == 'null':
            self.banner = 'banners/no-banner-available.jpg'
        super(Movie, self).save(*args, **kwargs)

    def images(self, *args, **kwargs):
        if self.image == 'null':
            self.image = 'movies/poster-not-available.jpg'
        super(Movie, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Movie, self).save(*args, **kwargs)

    def rating(self):
        ratings = self.rating_set.all()
        average = ratings.aggregate(Avg('rating'))
        return round(average['rating__avg'], 2) if ratings.count() > 0 else 0

    class Meta:
        db_table = 'movie'
        app_label = 'movie'

    def __str__(self):
        return f"{self.title}"


LINK_CHOICES = (
    ('download', 'DOWNLOAD LINK'),
    ('watch', 'WATCH LINK'),
)


class MovieLink(models.Model):
    movie = models.ForeignKey(Movie, related_name='movie_watch_link', on_delete=models.CASCADE)
    type = models.CharField(choices=LINK_CHOICES, max_length=10)
    link = models.URLField()

    def __str__(self):
        return f"{self.movie}"


class Rating(models.Model):
    RATE_CHOICES = (
        (10, "perfect"),
        (9, "extraordinary"),
        (8, "excellent"),
        (7, "very good"),
        (6, "good"),
        (5, "not bad"),
        (4, "ok"),
        (3, "bad"),
        (2, "really bad"),
        (1, "sucks!"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True)
    rating = models.PositiveIntegerField(choices=RATE_CHOICES)

    def __str__(self):
        return f"{self.rating}"


class History(models.Model):
    user = models.ForeignKey(User, related_name='history', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("user", "movie"),)

    def __str__(self):
        return f"{self.movie}"


class WatchList(models.Model):
    user = models.ForeignKey(User, related_name='watchlist', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    important = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("user", "movie"),)

    def __str__(self):
        return f"{self.movie}"


class BlockList(models.Model):
    user = models.ForeignKey(User, related_name='blocklist', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("user", "movie"),)

    def __str__(self):
        return f"{self.user}, {self.movie}"


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    action = models.CharField(max_length=128)
    created = models.DateTimeField(default=timezone.now)

    @classmethod
    def add(cls, user, movie, action, created=None):
        a = timezone.now()
        if created:
            a = created

        Activity(
            user=user,
            movie=movie,
            action=action,
            created=a,
        ).save()

    def __str__(self):
        return f"{self.user}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='movie_comments', on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        unique_together = (("user", "movie"),)

    def __str__(self):
        return 'Comment {} by {}'.format(self.comment, self.user)


class MovieCast(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    played_as = models.CharField(blank=True, null=True, max_length=256)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = (("person", "movie"),)

    def __str__(self):
        return f"{self.person}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(null=True, blank=True, max_length=128)
    address = models.CharField(null=True, blank=True, max_length=128)
    # country = CountryField()
    favorite_category = MultiSelectField(choices=CATEGORY_CHOICES, null=True, blank=True)
    favorite_movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'userprofile'

    def __str__(self):
        return f"{self.user.username.capitalize()} Profile"

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)
