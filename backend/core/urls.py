from django.urls import path

from .views import InterviewListView

app_name = "core"

urlpatterns = [
    path("", InterviewListView.as_view(), name="interview_list"),
]


