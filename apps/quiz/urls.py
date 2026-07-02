from django.urls import path

from .views import DailyQuizView, StartTestView, SubmitTestView, TestResultView

urlpatterns = [
    path("sessions/", StartTestView.as_view(), name="quiz-start"),
    path("daily/", DailyQuizView.as_view(), name="quiz-daily"),
    path("sessions/<uuid:session_id>/submit/", SubmitTestView.as_view(), name="quiz-submit"),
    path("sessions/<uuid:session_id>/", TestResultView.as_view(), name="quiz-result"),
]
