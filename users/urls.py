from django.urls import path
from .views import *


urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', LoginRefreshView.as_view(), name='refresh'),
    path('logout/', LogOutView.as_view(), name='logout'),

    path('forgot/', ForgotPasswordView.as_view(), name='forgot'),
    path('reset/', ResetPasswordView.as_view(), name='reset'),

    path('list/', UserListAPIView.as_view(), name='users-list'),
    path('students-list/', StudentListAPIView.as_view(), name='students-list'),
    path('teachers-list/', TeacherListAPIView.as_view(), name='teachers-list'),

    path('verify/', VerifyAPIView.as_view(), name='verify'),
    path('new-verify/', GetNewVerification.as_view(), name='new-verify'),

    path('change-user/', ChangeUserInformationView.as_view(), name='change-user'),
]
