from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path("chat/", include("chat.urls")),
    path("admin/", admin.site.urls),
)
