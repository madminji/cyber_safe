from django.db.models import Count, IntegerField, Q, Value
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Course, Lesson, LessonProgress
from .serializers import (
    CourseDetailSerializer,
    CourseListSerializer,
    LessonAnswerResultSerializer,
    LessonAnswerSerializer,
    LessonDetailSerializer,
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
    )


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
            lesson = Lesson.objects.select_related(
                "course",
                "question",
            ).prefetch_related("question__choices").get(
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
        return Response(
            self.get_serializer(
                lesson,
                context={
                    "language": requested_language(request),
                    "completed": completed,
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
