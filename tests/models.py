# from django.db import models
#
# from courses.models import Course
# from users.models import BaseModel, User
#
#
# class TestModel(BaseModel):
#     title = models.CharField(max_length=100)
#     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tests')
#
#     def __str__(self):
#         return self.title
#
#
# class Question(BaseModel):
#     test = models.ForeignKey(TestModel, on_delete=models.CASCADE, related_name='questions')
#     question = models.TextField()
#     options = models.JSONField()
#     correct_answers = models.JSONField()
#
#     def __str__(self):
#         return self.question
#
#
# class TestSubmission(BaseModel):
#     student = models.ForeignKey(User, related_name='submissions', on_delete=models.CASCADE)
#     test = models.ForeignKey(TestModel, related_name='submissions', on_delete=models.CASCADE)
#     answers = models.JSONField()
#     score = models.FloatField()
#     ai_feedback = models.TextField(null=True, blank=True)
#
#     def __str__(self):
#         return f"{self.student.username} - {self.test.title}"
#
