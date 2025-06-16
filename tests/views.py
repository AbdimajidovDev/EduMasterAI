# from django.shortcuts import render
# from rest_framework import viewsets
# from tests.models import TestSubmission, TestModel, Question
# from tests.serializers import TestSubmissionSerializer, TestModelSerializer, QuestionSerializer
#
#
# class TestViewSet(viewsets.ModelViewSet):
#     queryset = TestModel.objects.all()
#     serializer_class = TestModelSerializer
#
#
# class QuestionViewSet(viewsets.ModelViewSet):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer
#
#
# class TestSubmissionViewSet(viewsets.ModelViewSet):
#     queryset = TestSubmission.objects.all()
#     serializer_class = TestSubmissionSerializer
#
#     def get_queryset(self):
#         return TestSubmission.objects.filter(student=self.request.user)
#
#
