import json

from django.http import HttpResponse
from django.db.models import Count, IntegerField, Q, Value
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsModeratorOrAdmin

from .exporter import lesson_to_payload
from .importer import import_lesson_from_payload, parse_lesson_import_file
from .models import Course, Lesson, LessonProgress
from .serializers import (
    CourseDetailSerializer,
    CourseListSerializer,
    LessonAnswerResultSerializer,
    LessonAnswerSerializer,
    LessonDetailSerializer,
    LessonImportUploadSerializer,
)
from .services import submit_lesson_answer


def requested_language(request):
    language = request.query_params.get("language")
    if language in {"ru", "uz"}:
        return language
    if request.user.is_authenticated:
        return request.user.language
    return "ru"


def course_queryset(user):
    if user.is_authenticated:
        completed_lessons = Count(
            "lessons",
            filter=Q(
                lessons__is_published=True,
                lessons__progress_records__user=user,
            ),
            distinct=True,
        )
    else:
        completed_lessons = Value(0, output_field=IntegerField())
    return Course.objects.filter(is_published=True).annotate(
        lessons_count=Count("lessons", filter=Q(lessons__is_published=True), distinct=True),
        completed_lessons=completed_lessons,
    ).order_by("order", "title_ru")


class CourseListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseListSerializer

    @extend_schema(operation_id="courses_list")
    def get(self, request):
        language = requested_language(request)
        courses = course_queryset(request.user)
        return Response(
            self.get_serializer(courses, many=True, context={"language": language}).data
        )


class CourseDetailView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseDetailSerializer

    @extend_schema(operation_id="course_detail")
    def get(self, request, course_id):
        try:
            course = course_queryset(request.user).prefetch_related(
                "lessons"
            ).get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=404)
        completed_ids = set()
        if request.user.is_authenticated:
            completed_ids = set(
                LessonProgress.objects.filter(
                    user=request.user,
                    lesson__course=course,
                ).values_list("lesson_id", flat=True)
            )
        context = {
            "language": requested_language(request),
            "completed_ids": completed_ids,
        }
        return Response(self.get_serializer(course, context=context).data)


class LessonDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonDetailSerializer

    @extend_schema(operation_id="course_lesson_detail")
    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.select_related("course").prefetch_related(
                "questions__choices",
                "blocks",
                "tasks",
            ).get(
                id=lesson_id,
                is_published=True,
                course__is_published=True,
            )
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found."}, status=404)
        completed = LessonProgress.objects.filter(
            user=request.user,
            lesson=lesson,
        ).exists()
        completed_ids = set(
            LessonProgress.objects.filter(
                user=request.user,
                lesson__course=lesson.course,
            ).values_list("lesson_id", flat=True)
        )
        return Response(
            self.get_serializer(
                lesson,
                context={
                    "language": requested_language(request),
                    "completed": completed,
                    "completed_ids": completed_ids,
                },
            ).data
        )


class LessonAnswerView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonAnswerSerializer

    @extend_schema(
        operation_id="course_lesson_answer",
        responses=LessonAnswerResultSerializer,
    )
    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(
                id=lesson_id,
                is_published=True,
                course__is_published=True,
            )
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found."}, status=404)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = submit_lesson_answer(
            user=request.user,
            lesson=lesson,
            choice_id=serializer.validated_data["choice_id"],
        )
        return Response(result)


class LessonImportView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = LessonImportUploadSerializer

    @extend_schema(operation_id="admin_lesson_import")
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get("file"):
            payload = parse_lesson_import_file(serializer.validated_data["file"])
        else:
            payload = serializer.validated_data["payload"]
        result = import_lesson_from_payload(payload)
        return Response(
            {
                "status": "created" if result.created else "updated",
                "lesson_id": result.lesson.id,
                "lesson_slug": result.lesson.slug,
                "course_id": result.lesson.course_id,
                "blocks_count": result.blocks_count,
                "tasks_count": result.tasks_count,
                "questions_count": result.questions_count,
            },
            status=201 if result.created else 200,
        )


class AdminCourseContentView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]

    @extend_schema(operation_id="admin_course_content")
    def get(self, request):
        courses = Course.objects.prefetch_related("lessons").order_by("order", "title_ru")
        return Response(
            [
                {
                    "id": course.id,
                    "slug": course.slug,
                    "title": course.title_ru,
                    "level": course.level,
                    "is_published": course.is_published,
                    "lessons_count": course.lessons.count(),
                    "lessons": [
                        {
                            "id": lesson.id,
                            "slug": lesson.slug,
                            "title": lesson.title_ru,
                            "summary": lesson.summary_ru,
                            "module_title": lesson.module_title_ru,
                            "order": lesson.order,
                            "duration_minutes": lesson.duration_minutes,
                            "is_published": lesson.is_published,
                        }
                        for lesson in course.lessons.all()
                    ],
                }
                for course in courses
            ]
        )


class AdminLessonExportView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]

    @extend_schema(operation_id="admin_lesson_export")
    def get(self, request, lesson_id):
        try:
            lesson = Lesson.objects.select_related("course").prefetch_related(
                "blocks",
                "tasks",
                "questions__choices",
            ).get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found."}, status=404)

        payload = lesson_to_payload(lesson)
        response = HttpResponse(
            json.dumps(payload, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{lesson.order:02d}-{lesson.slug or lesson.id}.json"'
        )
        return response


class AdminLessonDeleteView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]

    @extend_schema(operation_id="admin_lesson_delete")
    def delete(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({"detail": "Lesson not found."}, status=404)
        lesson.delete()
        return Response(status=204)
