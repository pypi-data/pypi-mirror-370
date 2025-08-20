from . import views
from .django_compat import patterns, re_path

urlpatterns = patterns(
    "",
    re_path(r"^metrics/?$", views.metrics),
)
