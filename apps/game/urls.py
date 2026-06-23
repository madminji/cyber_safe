from django.urls import path

from .views import (
    AnswerGameView,
    GameResultView,
    GameSessionView,
    ScenarioListView,
    StartGameView,
)

urlpatterns = [
    path("scenarios/", ScenarioListView.as_view(), name="game-scenarios"),
    path("sessions/", StartGameView.as_view(), name="game-start"),
    path("sessions/<uuid:session_id>/", GameSessionView.as_view(), name="game-session"),
    path(
        "sessions/<uuid:session_id>/answer/",
        AnswerGameView.as_view(),
        name="game-answer",
    ),
    path(
        "sessions/<uuid:session_id>/result/",
        GameResultView.as_view(),
        name="game-result",
    ),
]

