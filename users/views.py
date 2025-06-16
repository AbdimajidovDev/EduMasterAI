from datetime import datetime
from tokenize import TokenError

from django.core.exceptions import ObjectDoesNotExist
from django.template.context_processors import request
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import ListAPIView, CreateAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_phone_code
from users.models import User, CODE_VERIFIED, DONE, NEW
from users.serializers import (SignUpSerializer,
                               ChangeUserInformationSerializer,
                               LoginSerializer,
                               LoginRefreshSerializer,
                               LogoutSerializer,
                               ForgotPasswordSerializer,
                               ResetPasswordSerializer)


# User  ----------------------------------->

class CreateUserView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


class UserListAPIView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


class TeacherListAPIView(ListAPIView):
    serializer_class = SignUpSerializer
    queryset = User.objects.filter(role='teacher')


class StudentListAPIView(ListAPIView):
    serializer_class = SignUpSerializer
    queryset = User.objects.filter(role='student')


# Verify code ------------------------------------------->

class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = request.data.get('code')

        self.check_verify(user, code)
        return Response(
            data={
                'succes': True,
                'auth_status': user.auth_status,
                'access': user.token()['access'],
                'refresh': user.token()['refresh'],
            }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        print(verifies)
        if not verifies.exists():
            data = {
                "message": "Tasdiqlash kodingiz xato yoki eskirgan"
            }
            raise ValidationError(data)
        verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True


# Get New Verify code ------------------------------------------->

class GetNewVerification(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        code = user.create_verify_code()
        send_phone_code(user.phone_number, code)
        return Response(
            {
                'succes': True,
                'message': "Tasdiqlash kodingiz qaytadan jo'natildi!"
            }
        )

    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                'message': "Kodingiz hali ishlatish uchun yaroqli. Biroz kuting!"
            }
            raise ValidationError(data)


# Change User Information ------------------------------------------->

class ChangeUserInformationView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeUserInformationSerializer
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.request.user
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        data = {
            'success': True,
            'auth_status': user.auth_status,
            'message': "User updated successfully",
        }
        return Response(data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        user = self.request.user
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        data = {
            'success': True,
            'auth_status': user.auth_status,
            'message': "User updated successfully",
        }
        return Response(data, status=status.HTTP_200_OK)


# Login, Log out ------------------------------------------------->

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogOutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                'success': True,
                'message': "You are logged out"
            }
            return Response(data, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({
                'success': False,
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


# Forgot Password -------------------------------------------->

class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get('phone_number')
        user = serializer.validated_data.get('user')
        print('phone and user in views')
        print(phone_number)
        print(user)

        if phone_number:
            code = user.create_verify_code()
            send_phone_code(phone_number, code)

        return Response({
            'success': True,
            'message': "Tassdiqlash kodi muvofaqiyatli jo'natildi!",
            'access': user.token()['access'],
            'refresh': user.token()['refresh'],
            'auth_status': user.auth_status
        })


# Reset Password ------------------------------------------------>

class ResetPasswordView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ResetPasswordSerializer
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).update(request, *args, **kwargs)
        print('response', response)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(str(e))
        return Response({
            'success': True,
            'message': "Parolingiz muvofaqiyatli o'zgartirildi!",
            'access': user.token()['access'],
            'refresh':  user.token()['refresh']
        })
