from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = i18n_patterns(
    path("chat/", include("chat.urls")),
    path("", RedirectView.as_view(pattern_name="chat:index")),
    path("admin/", admin.site.urls),
    path("rosetta/", include("rosetta.urls")),
)
