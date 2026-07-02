import tempfile
from pathlib import Path

from django import forms
from django.contrib import admin, messages
from django.core.management import call_command
from django.shortcuts import redirect, render
from django.urls import path

from .models import (
    Course,
    Lesson,
    LessonBlock,
    LessonChoice,
    LessonProgress,
    LessonQuestion,
    LessonTask,
)


class CourseImportForm(forms.Form):
    docx_file = forms.FileField(
        label="DOCX-файл с уроками",
        help_text=(
            "Загрузите подготовленный Word-файл. Импорт обновит три уровня: "
            "Basic, Advanced и Expert."
        ),
    )


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = (
        "order",
        "module_title_ru",
        "title_ru",
        "duration_minutes",
        "is_published",
    )
    readonly_fields = ()
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    change_list_template = "admin/courses/course/change_list.html"
    list_display = (
        "order",
        "title_ru",
        "level",
        "lessons_total",
        "duration_minutes",
        "is_published",
        "updated_at",
    )
    list_display_links = ("title_ru",)
    list_editable = ("order", "is_published")
    list_filter = ("level", "is_published")
    search_fields = ("title_ru", "title_uz", "description_ru", "description_uz")
    prepopulated_fields = {"slug": ("title_ru",)}
    inlines = (LessonInline,)
    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "slug",
                    "level",
                    "order",
                    "duration_minutes",
                    "is_published",
                )
            },
        ),
        (
            "Русский",
            {"fields": ("title_ru", "description_ru")},
        ),
        (
            "O‘zbekcha",
            {"fields": ("title_uz", "description_uz")},
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-docx/",
                self.admin_site.admin_view(self.import_docx_view),
                name="courses_course_import_docx",
            )
        ]
        return custom_urls + urls

    def import_docx_view(self, request):
        if request.method == "POST":
            form = CourseImportForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.cleaned_data["docx_file"]
                with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp:
                    for chunk in uploaded_file.chunks():
                        temp.write(chunk)
                    temp_path = Path(temp.name)
                try:
                    call_command("import_course_docx", str(temp_path))
                finally:
                    temp_path.unlink(missing_ok=True)
                self.message_user(
                    request,
                    "Курсы успешно импортированы из DOCX.",
                    level=messages.SUCCESS,
                )
                return redirect("admin:courses_course_changelist")
        else:
            form = CourseImportForm()
        context = {
            **self.admin_site.each_context(request),
            "title": "Импорт уроков из DOCX",
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/courses/course/import_docx.html", context)

    @admin.display(description="Уроков")
    def lessons_total(self, obj):
        return obj.lessons.count()


class LessonQuestionInline(admin.StackedInline):
    model = LessonQuestion
    extra = 0
    fieldsets = (
        ("Вопрос RU", {"fields": ("order", "text_ru", "explanation_ru")}),
        ("Вопрос UZ", {"fields": ("text_uz", "explanation_uz")}),
    )


class LessonBlockInline(admin.StackedInline):
    model = LessonBlock
    extra = 0
    fields = ("order", "type", "title_ru", "body_ru", "title_uz", "body_uz", "data")


class LessonTaskInline(admin.StackedInline):
    model = LessonTask
    extra = 0
    fields = (
        "order",
        "type",
        "title_ru",
        "instruction_ru",
        "title_uz",
        "instruction_uz",
        "data",
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "order",
        "slug",
        "title_ru",
        "module_title_ru",
        "duration_minutes",
        "is_published",
        "has_question",
        "has_video",
    )
    list_display_links = ("title_ru",)
    list_editable = ("order", "is_published")
    list_filter = ("course", "is_published")
    search_fields = (
        "slug",
        "title_ru",
        "title_uz",
        "summary_ru",
        "summary_uz",
        "content_ru",
        "content_uz",
    )
    autocomplete_fields = ("course",)
    inlines = (LessonBlockInline, LessonTaskInline, LessonQuestionInline)
    fieldsets = (
        (
            "Структура",
            {
                "fields": (
                    "course",
                    "slug",
                    "order",
                    "duration_minutes",
                    "is_published",
                )
            },
        ),
        (
            "Русский контент",
            {
                "fields": (
                    "module_title_ru",
                    "module_slug",
                    "title_ru",
                    "summary_ru",
                    "content_ru",
                    "video_url_ru",
                )
            },
        ),
        (
            "O‘zbekcha kontent",
            {
                "fields": (
                    "module_title_uz",
                    "title_uz",
                    "summary_uz",
                    "content_uz",
                    "video_url_uz",
                )
            },
        ),
    )

    @admin.display(boolean=True, description="Вопрос")
    def has_question(self, obj):
        return obj.questions.exists()

    @admin.display(boolean=True, description="Видео")
    def has_video(self, obj):
        return bool(obj.video_url_ru or obj.video_url_uz)


class LessonChoiceInline(admin.TabularInline):
    model = LessonChoice
    extra = 4
    fields = ("order", "text_ru", "text_uz", "is_correct")


@admin.register(LessonQuestion)
class LessonQuestionAdmin(admin.ModelAdmin):
    list_display = ("lesson", "order", "short_text", "choices_total")
    list_editable = ("order",)
    search_fields = ("text_ru", "text_uz", "lesson__title_ru")
    autocomplete_fields = ("lesson",)
    inlines = (LessonChoiceInline,)

    @admin.display(description="Вопрос")
    def short_text(self, obj):
        return obj.text_ru[:100]

    @admin.display(description="Вариантов")
    def choices_total(self, obj):
        return obj.choices.count()


@admin.register(LessonBlock)
class LessonBlockAdmin(admin.ModelAdmin):
    list_display = ("lesson", "order", "type", "title_ru")
    list_editable = ("order",)
    list_filter = ("type", "lesson__course")
    search_fields = ("title_ru", "body_ru", "lesson__title_ru")
    autocomplete_fields = ("lesson",)


@admin.register(LessonTask)
class LessonTaskAdmin(admin.ModelAdmin):
    list_display = ("lesson", "order", "type", "title_ru")
    list_editable = ("order",)
    list_filter = ("type", "lesson__course")
    search_fields = ("title_ru", "instruction_ru", "lesson__title_ru")
    autocomplete_fields = ("lesson",)


@admin.register(LessonChoice)
class LessonChoiceAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "text_ru", "is_correct")
    list_editable = ("order", "is_correct")
    list_filter = ("is_correct", "question__lesson__course")
    search_fields = ("text_ru", "text_uz", "question__text_ru")
    autocomplete_fields = ("question",)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed_at")
    list_filter = ("completed_at", "lesson__course")
    search_fields = ("user__full_name", "user__phone", "lesson__title_ru")
    autocomplete_fields = ("user", "lesson")
    readonly_fields = ("completed_at",)
