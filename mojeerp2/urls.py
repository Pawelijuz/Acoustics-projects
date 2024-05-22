from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from komunikator import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('projekty/', include('komunikator.urls')),
    path('login/', auth_views.LoginView.as_view(), name="login"),
    path('members/', include('django.contrib.auth.urls')),
    path('members/', include('members.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#dzięki include wczytają nam się wszystkie urls z "komunikatora"


