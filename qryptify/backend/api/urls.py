from django.urls import path
from home.views import (
    LoginAPI,SignupAPI,
    get_csrf_token,
    UserDetailsAPI,
    LogoutAPI,RefreshTokenAPI,
    EmailAPI,UpdateUserDetailsAPI,
    AnalyzeUserInputAPI,
    ResetPasswordAPI,
    DeleteAccountUserAPI,
    GetAccessTokenAPI,
    GetLogsAPI,
    UsageLogAPI
    )


urlpatterns=[  
    path('login/',LoginAPI.as_view()),
    path('signup/',SignupAPI.as_view()),
    path('csrf-token/',get_csrf_token),
    path('user-details/',UserDetailsAPI.as_view()),
    path('logout/',LogoutAPI.as_view()),
    path('refresh-token/',RefreshTokenAPI.as_view()),
    path('issue-mail/',EmailAPI.as_view()),
    path('forgot-password/',LoginAPI.as_view()),
    path('update-profile/',UpdateUserDetailsAPI.as_view()),
    path('analyze-input-file/',AnalyzeUserInputAPI.as_view()),
    path('reset-password/',ResetPasswordAPI.as_view()),
    path('user-account-delete/',DeleteAccountUserAPI.as_view()),
    path('get-access-token/', GetAccessTokenAPI.as_view(), name='get-access-token'),
    path('getlogs/',GetLogsAPI.as_view()),
    path('block-data/',UsageLogAPI.as_view())
]