import random
import uuid

from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.core.validators import FileExtensionValidator
from django.db import models
from datetime import datetime, timedelta

from rest_framework_simplejwt.tokens import RefreshToken

from users.models.misc import BaseModel, UserManager


ADMIN , TEACHER, STUDENT= ( 'admin', 'teacher', 'student')
NEW, CODE_VERIFIED, DONE = ('new', 'code_verified', 'done')


class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    USER_ROLES = (
        (ADMIN, ADMIN),
        (TEACHER, TEACHER),
        (STUDENT, STUDENT),
    )

    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=13, unique=True)
    role = models.CharField(max_length=33, choices=USER_ROLES, default=STUDENT)
    auth_status = models.CharField(max_length=33, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic'])])

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

    def set_status(self, new_status):
        if new_status not in dict(self.AUTH_STATUS):
            raise ValueError('Invalid status')
        self.status = new_status
        self.save()

    def is_transition_allowed(self, new_status):
        allowed_transitions = {
            NEW: [CODE_VERIFIED],
            CODE_VERIFIED: [DONE],
        }
        return new_status in allowed_transitions.get(self.status, [])


    def create_verify_code(self):
        code = ''.join([str(random.randint(0, 100) % 10) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            code=code,
        )
        return code

    def check_pass(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    def save(self, *args, **kwargs):
        if not self.pk:
            self.check_pass()
            self.hashing_password()
        super(User, self).save(*args, **kwargs)


EXPIRE_TIME = 2

class UserConfirmation(BaseModel):
    code = models.CharField(max_length=4)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        self.expiration_time = datetime.now() + timedelta(minutes=EXPIRE_TIME)
        super(UserConfirmation, self).save(*args, **kwargs)
