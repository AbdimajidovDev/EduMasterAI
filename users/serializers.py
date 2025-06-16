import phonenumbers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from shared.utility import send_phone_code
from users.models import User, UserConfirmation, NEW, CODE_VERIFIED, DONE
from rest_framework import exceptions
import re


phone_regex = re.compile(r"(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+")



class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'role', 'password', 'auth_status')
        extra_kwargs = {'phone_number': {'validators': []}}

    def create(self, validated_data):
        password = self.validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        code = user.create_verify_code()
        send_phone_code(user.phone_number, code)
        return user

    def validate_phone_number(self, phone_number):

        if not phone_number:
            data = {
                'success': False,
                'message': "Telefon raqam kiritish majburiy!"
            }
            raise ValidationError(data)

        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            data = {
                'success': False,
                'message': "Bu raqam orqali allaqachon ro'yxatdan o'tilgan!"
            }
            raise ValidationError(data)

        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                print('check phonenumbers: ', phonenumbers.is_valid_number(parsed_number))
                data = {
                    'success': False,
                    'message': "Telefon raqam noto'g'ri!"
                }
                raise ValidationError(data)
        except phonenumbers.NumberParseException:
            data = {
                'success': False,
                'data': "Telefon raqamingiz noto'g'ri formatda! (It's True format: +998xxxxxxxxx)",
            }
            raise ValidationError(data)
        return phone_number

    def to_representation(self, instance):
        print('to_rep', instance)
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data

class ChangeUserInformationSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)


    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        first_name = data.get('first_name', None)
        last_name = data.get('last_name', None)

        print(first_name, last_name, password, confirm_password)

        if password != confirm_password:
            raise ValidationError({
                'message': "Parolingiz va tasdiqlash parolingiz bir-biriga teng emas!"
            })

        if password:
            validate_password(password)

    #     if first_name == last_name:
    #         raise ValidationError({
    #             'data': "Ism va Familiya bir xil bo'lishi mumkin emas!"
    #         })
    #
    #     if (len(first_name) < 2 or len(first_name) > 25):
    #         raise ValidationError({
    #             'message': "Ism uzunligi 5 dan 25 gacha bo'lishi kerak!"
    #         })
    #     if len(last_name) < 2 or len(last_name) > 25:
    #         raise ValidationError({
    #             'message': "Familiya uzunligi 5 dan 25 gacha bo'lishi kerak!"
    #         })
    #
    #     if first_name.isdigit():
    #         raise ValidationError({
    #             'message': "Ismda raqamlar qatnashishi mumkin emas!"
    #         })
    #     if last_name.isdigit():
    #         raise ValidationError({
    #             'message': "Familiyada raqamlar qatnashishi mumkin emas!"
    #         })
    #
        return data

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.password = validated_data.get('confirm_password', instance.password)

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))

        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE

        instance.save()
        return instance


    def validate_phone_number(self, phone_number):
        print(phone_number)
        print(len(phone_number))
        request = self.context.get('request')

        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            if phone_number != request.user.phone_number:
                raise ValidationError({
                    'success': False,
                    'message': "Bunday raqam orqali ro'yxatdan allaqachon o'tilgan"
                })
        try:
            phone = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(phone):
                raise ValidationError({
                    'success': False,
                    'message': "Telefon raqam noto'g'ri!"
                })
        except phonenumbers.NumberParseException:
            raise ValidationError({
                'success': False,
                'message': "Telefon raqam noto'g'ri formatda! (It's True format: +998xxxxxxxxx)!"
            })
        return phone_number


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['phone_number'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def validate(self, data):
        self.auth_validate(data)

        if self.user.auth_status != DONE:
            raise PermissionError("Siz login qila olmaysi. Ruxsatingiz yo'q!")
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        data['full_name'] = self.user.full_name
        return data

    def auth_validate(self, data):
        print('login data: ', data)
        phone = data.get('phone_number')
        password = data.get('password')

        if not phone or not password:
            data = {
                'success': False,
                'message': "Telefon raqam va parol kiritilishi shart!"
            }
            raise ValidationError(data)

        current_user = User.objects.filter(phone_number=phone).first()

        if current_user is not None and current_user.auth_status in [NEW, CODE_VERIFIED]:
            raise ValidationError({
                'success': False,
                'message': "Siz ro'yxatdan to'liq o'tmagansiz!"
            })

        user = authenticate(phone_number=phone, password=password)

        if user is None:
            raise ValidationError({
                'success': False,
                'message': "Login yoki parolingiz noto'g'ri!"
            })

        self.user = user

    def get_user(self, **kwargs):
        user = User.objects.filter(**kwargs).first()

        if not user:
            raise ValidationError({
                'message': "Foydalanuvchi topilmadi!"
            })
        return user


class LoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    if phone_number is None:
        raise ValidationError({
            'success': False,
            'message': "Siz telefon raqamingizni kiritishingiz kerak!"
        })

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')

        try:
            phone = phonenumbers.parse(phone_number, None) # +998
            if not phonenumbers.is_valid_number(phone):
                raise ValidationError({
                    'success': False,
                    'message': "Telefon raqam noto'g'ri."
                })
        except phonenumbers.NumberParseException:
            raise ValidationError({
                'success': False,
                'message': "Telefon raqam noto'g'ri formatda. It's True formati: +998xxxxxxxxx."
            })

        user = User.objects.filter(phone_number=phone_number)

        if not user.exists():
            raise ValidationError({
                'success': False,
                'message': "Foydalanuvchi topilmadi!"
            })
        attrs['user'] = user.first()
        return attrs

class ResetPasswordSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    password = serializers.CharField(required=False)
    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('id', 'password', 'confirm_password')

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise ValidationError({
                'success': False,
                'message': "Parolingiz va tasdiqlash parolingiz bir-biriga teng emas!"
            })

        if password:
            validate_password(password)
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        return super(ResetPasswordSeralizer, self).update(instance, validated_data)
