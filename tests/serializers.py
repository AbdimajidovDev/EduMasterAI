# from django.db import models
# from rest_framework import serializers
#
# from tests.models import TestModel, Question, TestSubmissions
#
#
# class TestModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TestModel
#         fields = '__all__'
#
#
# class QuestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Question
#         fields = '__all__'
#
#
# class TestSubmissionSerializer(serializers.ModelSerializer):
#     answers = serializers.SerializerMethodField()
#     score = models.FloatField()
#     ai_feedback = models.TextField()
#
#     def get_answers(self, obj):
#         answers = obj.answers.all()
#         return answers.order_by('score')
#
#     def get_score(self, obj):
#         return obj.score
#
#     class Meta:
#         model = TestSubmissions
#         fields = '__all__'
