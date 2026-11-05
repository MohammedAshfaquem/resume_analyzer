from django.urls import include, path


urlpatterns = [path("", include("apps.analyzer.urls"))]
