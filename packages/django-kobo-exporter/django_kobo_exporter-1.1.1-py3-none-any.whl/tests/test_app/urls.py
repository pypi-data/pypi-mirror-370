from django.conf.urls import include

from kobo_exporter.django_compat import patterns, re_path

urlpatterns = patterns(
    "",
    re_path(r"^kobo_exporter/", include("kobo_exporter.urls")),
)
