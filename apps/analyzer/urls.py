from django.urls import path

from .views import resume_analyzer


urlpatterns = [path("", resume_analyzer, name="resume_analyzer")]
