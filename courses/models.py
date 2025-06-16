from django.core.validators import FileExtensionValidator
from django.db import models
from users.models import User
from users.models.misc import BaseModel


class Course(BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, unique_for_date='created_at')
    description = models.TextField()
    teacher = models.ForeignKey(User, related_name='courses', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Lesson(BaseModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    file = models.FileField(upload_to='lessons/%Y/%m/%d',
                            validators=[FileExtensionValidator(allowed_extensions=['mp4', 'pdf', 'docx', 'jpg', 'jpeg', 'png'])])
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.title} - {self.title}"
