from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/quiz/", include("apps.quiz.urls")),
    path("api/v1/certificates/", include("apps.certificates.urls")),
    path("api/v1/scammer-db/", include("apps.scammer_db.urls")),
    path("api/v1/analyzer/", include("apps.analyzer.urls")),
    path("api/v1/courses/", include("apps.courses.urls")),
    path("api/v1/game/", include("apps.game.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
]
