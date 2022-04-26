from django.urls import path
from .views import (
    FileUploadView,
    ChangeEmailView,
    UserEmailView,
    ChangePasswordView,
    UserDetailsView,
    SubscribeView,
    ImageRecognitionView,
    APIKeyView,
    ScraperView,
    EmailView,
    PhoneView,
    LinkView,
    GrammerView,
    IPView,
    HolidayView,
    EmailfinderView,
    LinkpreView,
    CancelSubscription
)

app_name = 'core'

urlpatterns = [
    path('demo/', FileUploadView.as_view(), name='file-upload-demo'),
    path('email/', UserEmailView.as_view(), name='email'),
    path('change-email/', ChangeEmailView.as_view(), name='change-email'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('billing/', UserDetailsView.as_view(), name='billing'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('cancel-subscription/', CancelSubscription.as_view(),
         name='cancel-subscription'),
    path('upload/', ImageRecognitionView.as_view(), name='image-recognition'),
    path('scraper/', ScraperView.as_view(), name='scraper'),
    path('email-verify/', EmailView.as_view(), name='email'),
    path('phone-verify/', PhoneView.as_view(), name='phone'),
    path('link-verify/', LinkView.as_view(), name='link'),
    path('grammer-checker/', GrammerView.as_view(), name='grammer'),
    path('ip-tracker/', IPView.as_view(), name='iptracker'),
    path('holiday/', HolidayView.as_view(), name='holiday'),
    path('email-finder/', EmailfinderView.as_view(), name='email'),
    path('link-preview/', LinkpreView.as_view(), name='preview'),
    path('api-key/', APIKeyView.as_view(), name='api-key')
]
