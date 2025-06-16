# from django.db import models
#
# from courses.models import Course
# from users.models import BaseModel, User
#
#
#
# class Assignment(BaseModel):
#     title = models.CharField(max_length=100)
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     description = models.TextField()
#
#
# class AssignmentFile(BaseModel):
#     file = models.FileField()
#     student = models.ForeignKey(User, on_delete=models.CASCADE)
#     assigment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
