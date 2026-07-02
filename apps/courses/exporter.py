from .models import Lesson


def localized(value_ru: str, value_uz: str) -> dict[str, str]:
    return {"ru": value_ru or "", "uz": value_uz or value_ru or ""}


def lesson_to_payload(lesson: Lesson) -> dict:
    blocks = []
    for block in lesson.blocks.all():
        block_payload = {
            "type": block.type,
            "order": block.order,
            "title": localized(block.title_ru, block.title_uz),
            "body": localized(block.body_ru, block.body_uz),
        }
        block_payload.update(block.data or {})
        blocks.append(block_payload)

    if not blocks and (lesson.content_ru or lesson.content_uz):
        blocks.append(
            {
                "type": "theory",
                "order": 1,
                "title": localized("Теория", "Nazariya"),
                "body": localized(lesson.content_ru, lesson.content_uz),
            }
        )

    tasks = [
        {
            "type": task.type,
            "order": task.order,
            "title": localized(task.title_ru, task.title_uz),
            "instruction": localized(task.instruction_ru, task.instruction_uz),
            "data": task.data or {},
        }
        for task in lesson.tasks.all()
    ]

    quiz = []
    for question in lesson.questions.all():
        quiz.append(
            {
                "order": question.order,
                "text": localized(question.text_ru, question.text_uz),
                "choices": [
                    {
                        "order": choice.order,
                        "text": localized(choice.text_ru, choice.text_uz),
                        "is_correct": choice.is_correct,
                    }
                    for choice in question.choices.all()
                ],
                "explanation": localized(
                    question.explanation_ru,
                    question.explanation_uz,
                ),
            }
        )

    return {
        "course_slug": lesson.course.slug,
        "lesson_slug": lesson.slug,
        "module": {
            "slug": lesson.module_slug,
            "title": localized(lesson.module_title_ru, lesson.module_title_uz),
        },
        "order": lesson.order,
        "title": localized(lesson.title_ru, lesson.title_uz),
        "summary": localized(lesson.summary_ru, lesson.summary_uz),
        "content": localized(lesson.content_ru, lesson.content_uz),
        "blocks": blocks,
        "tasks": tasks,
        "quiz": quiz,
        "video_url": localized(lesson.video_url_ru, lesson.video_url_uz),
        "duration_minutes": lesson.duration_minutes,
        "is_published": lesson.is_published,
    }
