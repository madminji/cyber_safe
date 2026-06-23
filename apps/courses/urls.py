from django.urls import path

from .views import CourseDetailView, CourseListView, LessonAnswerView, LessonDetailView

urlpatterns = [
    path("", CourseListView.as_view(), name="course-list"),
    path("<uuid:course_id>/", CourseDetailView.as_view(), name="course-detail"),
    path("lessons/<uuid:lesson_id>/", LessonDetailView.as_view(), name="lesson-detail"),
    path(
        "lessons/<uuid:lesson_id>/answer/",
        LessonAnswerView.as_view(),
        name="lesson-answer",
    ),
]

