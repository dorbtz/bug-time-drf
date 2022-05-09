from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin
from .models import *

# Register your models here.

# admin.site.register(Movie)
# admin.site.register(MovieLink)
# admin.site.register(Comment)
# admin.site.register(Activity)
admin.site.register(UserProfile)
admin.site.register(Rating)
admin.site.register(History)
admin.site.register(WatchList)
admin.site.register(BlockList)

TokenAdmin.raw_id_fields = ['user']


@admin.register(Movie)
class MovieModel(admin.ModelAdmin):
    list_filter = ('title', 'category', 'language', 'status')
    list_display = ('title', 'year_of_production')


@admin.register(MovieLink)
class MovieLinkModel(admin.ModelAdmin):
    list_filter = ['type']
    list_display = ('movie', 'type')


@admin.register(Person)
class PersonModel(admin.ModelAdmin):
    list_filter = ['name', 'gender']
    list_display = ('name', 'image', 'birthday', 'gender')


@admin.register(Comment)
class CommentModel(admin.ModelAdmin):
    list_filter = ['active', 'created_at']
    list_display = ('user', 'comment', 'movie', 'created_at', 'active')
    search_fields = ('user', 'comment')
    actions = ['approve_comments']

    @staticmethod
    def approve_comments(request, queryset):
        queryset.update(active=True)


@admin.register(Activity)
class CommentModel(admin.ModelAdmin):
    list_filter = ['action', 'movie']
    list_display = ('user', 'movie', 'action')


@admin.register(MovieCast)
class CommentModel(admin.ModelAdmin):
    list_filter = ['person', 'movie']
    list_display = ('person', 'movie')
