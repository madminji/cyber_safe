from django.urls import path

from .views import (
    AdminCourseContentView,
    AdminLessonDeleteView,
    AdminLessonExportView,
    CourseDetailView,
    CourseListView,
    LessonAnswerView,
    LessonDetailView,
    LessonImportView,
)

urlpatterns = [
    path("", CourseListView.as_view(), name="course-list"),
    path(
        "admin/lessons/import/",
        LessonImportView.as_view(),
        name="admin-lesson-import",
    ),
    path(
        "admin/content/",
        AdminCourseContentView.as_view(),
        name="admin-course-content",
    ),
    path(
        "admin/lessons/<uuid:lesson_id>/export/",
        AdminLessonExportView.as_view(),
        name="admin-lesson-export",
    ),
    path(
        "admin/lessons/<uuid:lesson_id>/",
        AdminLessonDeleteView.as_view(),
        name="admin-lesson-delete",
    ),
    path("<uuid:course_id>/", CourseDetailView.as_view(), name="course-detail"),
    path("lessons/<uuid:lesson_id>/", LessonDetailView.as_view(), name="lesson-detail"),
    path(
        "lessons/<uuid:lesson_id>/answer/",
        LessonAnswerView.as_view(),
        name="lesson-answer",
    ),
]
