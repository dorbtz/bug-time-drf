from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views

urlpatterns = [
    # path('', HomesView.as_view()),
    path('admin/', admin.site.urls),
    # path('movieslists/', include('movie.urls', namespace='movies')),

    # REST FRAMEWORK URLS
    path('', include('movie.api.urls')),
    # path('api-auth/', include('rest_framework.urls')),
    # path('login/', views.obtain_auth_token, name='login'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
