import uuid

from django.conf import settings
from django.db import models


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="certificates",
        on_delete=models.PROTECT,
    )
    quiz_session = models.OneToOneField(
        "quiz.TestSession",
        related_name="certificate",
        on_delete=models.PROTECT,
    )
    level = models.CharField(max_length=10)
    score = models.PositiveSmallIntegerField()
    issued_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

