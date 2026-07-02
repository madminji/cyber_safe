from django.urls import path

from .views import (
    CharacterListView,
    CompleteWebGameView,
    GameProfileView,
    LeaderboardView,
    SaveCharacterView,
    Scenario3DListView,
    StartWebGameView,
    SubmitActionView,
    WebGameResultView,
)

urlpatterns = [
    path("characters/", CharacterListView.as_view(), name="webgame-characters"),
    path("profile/", GameProfileView.as_view(), name="webgame-profile"),
    path(
        "profile/character/",
        SaveCharacterView.as_view(),
        name="webgame-profile-character",
    ),
    path("scenarios/", Scenario3DListView.as_view(), name="webgame-scenarios"),
    path("sessions/", StartWebGameView.as_view(), name="webgame-start"),
    path(
        "sessions/<uuid:session_id>/actions/",
        SubmitActionView.as_view(),
        name="webgame-action",
    ),
    path(
        "sessions/<uuid:session_id>/complete/",
        CompleteWebGameView.as_view(),
        name="webgame-complete",
    ),
    path(
        "sessions/<uuid:session_id>/result/",
        WebGameResultView.as_view(),
        name="webgame-result",
    ),
    path("leaderboard/", LeaderboardView.as_view(), name="webgame-leaderboard"),
]
