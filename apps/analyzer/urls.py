from django.urls import path

from .views import SMSAnalysisView, URLAnalysisView

urlpatterns = [
    path("url/", URLAnalysisView.as_view(), name="analyzer-url"),
    path("sms/", SMSAnalysisView.as_view(), name="analyzer-sms"),
]

